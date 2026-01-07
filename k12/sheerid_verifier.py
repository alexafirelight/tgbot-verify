"""SheerID teacher verification main module (ChatGPT Teacher K12)."""
import re
import random
import logging
import httpx
from typing import Dict, Optional, Tuple

# Support both package import and direct script execution
try:
    from . import config  # type: ignore
    from .name_generator import NameGenerator, generate_email, generate_birth_date  # type: ignore
    from .img_generator import generate_teacher_pdf, generate_teacher_png  # type: ignore
except ImportError:
    import config  # type: ignore
    from name_generator import NameGenerator, generate_email, generate_birth_date  # type: ignore
    from img_generator import generate_teacher_pdf, generate_teacher_png  # type: ignore

# Export configuration constants
PROGRAM_ID = config.PROGRAM_ID
SHEERID_BASE_URL = config.SHEERID_BASE_URL
MY_SHEERID_URL = config.MY_SHEERID_URL
SCHOOLS = config.SCHOOLS
DEFAULT_SCHOOL_ID = config.DEFAULT_SCHOOL_ID


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class SheerIDVerifier:
    """Teacher identity verifier for the SheerID API."""

    def __init__(self, verification_id: str):
        """
        Initialize the verifier.

        Args:
            verification_id: SheerID verification ID
        """
        self.verification_id = verification_id
        self.device_fingerprint = self._generate_device_fingerprint()
        self.http_client = httpx.Client(timeout=30.0)

    def __del__(self):
        """Clean up the HTTP client."""
        if hasattr(self, "http_client"):
            self.http_client.close()

    @staticmethod
    def _generate_device_fingerprint() -> str:
        """Generate a random device fingerprint."""
        chars = "0123456789abcdef"
        return "".join(random.choice(chars) for _ in range(32))

    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize the URL (currently a no-op)."""
        return url

    @staticmethod
    def parse_verification_id(url: str) -> Optional[str]:
        """Parse verification ID from URL."""
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def _sheerid_request(
        self, method: str, url: str, body: Optional[Dict] = None
    ) -> Tuple[Dict, int]:
        """Send a request to the SheerID API."""
        headers = {
            "Content-Type": "application/json",
        }

        try:
            response = self.http_client.request(
                method=method,
                url=url,
                json=body,
                headers=headers,
            )

            try:
                data = response.json()
            except Exception:
                data = response.text

            return data, response.status_code
        except Exception as e:
            logger.error("SheerID request failed: %s", e)
            raise

    def _upload_to_s3(self, upload_url: str, content: bytes, mime_type: str) -> bool:
        """Upload a file to S3-compatible storage."""
        try:
            headers = {
                "Content-Type": mime_type,
            }
            response = self.http_client.put(
                upload_url,
                content=content,
                headers=headers,
                timeout=60.0,
            )
            return 200 <= response.status_code < 300
        except Exception as e:
            logger.error("S3 upload failed: %s", e)
            return False

    def verify(
        self,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        birth_date: str = None,
        school_id: str = None,
        hcaptcha_token: str = None,
        turnstile_token: str = None,
    ) -> Dict:
        """
        Run the full verification flow without status polling (returns once docs are submitted).
        """
        try:
            current_step = "initial"

            # Generate teacher profile if not provided
            if not first_name or not last_name:
                name = NameGenerator.generate()
                first_name = name["first_name"]
                last_name = name["last_name"]

            school_id = school_id or DEFAULT_SCHOOL_ID
            school = SCHOOLS[school_id]

            if not email:
                email = generate_email()

            if not birth_date:
                birth_date = generate_birth_date()

            logger.info("Teacher: %s %s", first_name, last_name)
            logger.info("Email: %s", email)
            logger.info("School: %s", school["name"])
            logger.info("Birth date: %s", birth_date)
            logger.info("Verification ID: %s", self.verification_id)

            # Step 1: generate teacher proof PDF + PNG
            logger.info("Step 1/4: Generating teacher proof PDF and PNG...")
            pdf_data = generate_teacher_pdf(first_name, last_name)
            png_data = generate_teacher_png(first_name, last_name)
            pdf_size = len(pdf_data)
            png_size = len(png_data)
            logger.info(
                "✓ PDF size: %.2fKB, PNG size: %.2fKB",
                pdf_size / 1024,
                png_size / 1024,
            )

            # Step 2: submit teacher information
            logger.info("Step 2/4: Submitting teacher information...")
            step2_body = {
                "firstName": first_name,
                "lastName": last_name,
                "birthDate": birth_date,
                "email": email,
                "phoneNumber": "",
                "organization": {
                    "id": school["id"],
                    "idExtended": school["idExtended"],
                    "name": school["name"],
                },
                "deviceFingerprintHash": self.device_fingerprint,
                "locale": "en-US",
                "metadata": {
                    "marketConsentValue": False,
                    "refererUrl": f"{SHEERID_BASE_URL}/verify/{PROGRAM_ID}/?verificationId={self.verification_id}",
                    "verificationId": self.verification_id,
                    "submissionOptIn": (
                        "By submitting the personal information above, I acknowledge that my personal "
                        "information is being collected under the privacy policy of the business from which "
                        "I am seeking a discount"
                    ),
                },
            }

            step2_data, step2_status = self._sheerid_request(
                "POST",
                f"{SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectTeacherPersonalInfo",
                step2_body,
            )

            if step2_status != 200:
                raise Exception(f"Step 2 failed (status {step2_status}): {step2_data}")

            if step2_data.get("currentStep") == "error":
                error_msg = ", ".join(step2_data.get("errorIds", ["Unknown error"]))
                raise Exception(f"Step 2 error: {error_msg}")

            logger.info("✓ Step 2 completed: %s", step2_data.get("currentStep"))
            current_step = step2_data.get("currentStep", current_step)

            # Step 3: skip SSO (if required)
            if current_step in ["sso", "collectTeacherPersonalInfo"]:
                logger.info("Step 3/4: Skipping SSO verification...")
                step3_data, _ = self._sheerid_request(
                    "DELETE",
                    f"{SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/sso",
                )
                logger.info("✓ Step 3 completed: %s", step3_data.get("currentStep"))
                current_step = step3_data.get("currentStep", current_step)

            # Step 4: upload documents and complete submission
            logger.info("Step 4/4: Requesting upload URLs and uploading documents...")
            step4_body = {
                "files": [
                    {
                        "fileName": "teacher_document.pdf",
                        "mimeType": "application/pdf",
                        "fileSize": pdf_size,
                    },
                    {
                        "fileName": "teacher_document.png",
                        "mimeType": "image/png",
                        "fileSize": png_size,
                    },
                ]
            }

            step4_data, step4_status = self._sheerid_request(
                "POST",
                f"{SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/docUpload",
                step4_body,
            )

            documents = step4_data.get("documents") or []
            if len(documents) < 2:
                raise Exception("Failed to obtain upload URLs")

            pdf_upload_url = documents[0]["uploadUrl"]
            png_upload_url = documents[1]["uploadUrl"]
            logger.info("✓ Upload URLs obtained")

            if not self._upload_to_s3(pdf_upload_url, pdf_data, "application/pdf"):
                raise Exception("PDF upload failed")
            if not self._upload_to_s3(png_upload_url, png_data, "image/png"):
                raise Exception("PNG upload failed")
            logger.info("✓ Teacher proof PDF/PNG uploaded successfully")

            step6_data, _ = self._sheerid_request(
                "POST",
                f"{SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/completeDocUpload",
            )
            logger.info("✓ Document submission completed: %s", step6_data.get("currentStep"))
            final_status = step6_data

            # No status polling; just return "pending" and let caller check later if needed
            return {
                "success": True,
                "pending": True,
                "message": "Documents submitted; waiting for review",
                "verification_id": self.verification_id,
                "redirect_url": final_status.get("redirectUrl"),
                "status": final_status,
            }

        except Exception as e:
            logger.error("Verification failed: %s", e)
            return {
                "success": False,
                "message": str(e),
                "verification_id": self.verification_id,
            }
