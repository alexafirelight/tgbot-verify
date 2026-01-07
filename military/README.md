# ChatGPT Military SheerID Verification Approach

## 📋 Overview

The ChatGPT military verification flow differs from standard student/teacher verification.  
It requires calling an additional endpoint to collect military status information **before** submitting the personal information form.

## 🔄 Verification Flow

### Step 1: Collect Military Status (`collectMilitaryStatus`)

Before submitting the personal information form, you must call this endpoint to set the user's military status.

**Request:**
- **URL**: `https://services.sheerid.com/rest/v2/verification/{verificationId}/step/collectMilitaryStatus`
- **Method**: `POST`
- **Body**:
```json
{
    "status": "VETERAN" // one of 3 possible values
}
```

**Example Response:**
```json
{
    "verificationId": "{verification_id}",
    "currentStep": "collectInactiveMilitaryPersonalInfo",
    "errorIds": [],
    "segment": "military",
    "subSegment": "veteran",
    "locale": "en-US",
    "country": null,
    "created": 1766539517800,
    "updated": 1766540141435,
    "submissionUrl": "https://services.sheerid.com/rest/v2/verification/{verification_id}/step/collectInactiveMilitaryPersonalInfo",
    "instantMatchAttempts": 0
}
```

**Key fields:**
- `submissionUrl`: the URL that must be used in the next step to submit personal info
- `currentStep`: should become `collectInactiveMilitaryPersonalInfo` after this call

---

### Step 2: Collect Inactive Military Personal Info (`collectInactiveMilitaryPersonalInfo`)

Use the `submissionUrl` returned from Step 1 to submit personal information.

**Request:**
- **URL**: taken from the `submissionUrl` field of Step 1  
  e.g. `https://services.sheerid.com/rest/v2/verification/{verificationId}/step/collectInactiveMilitaryPersonalInfo`
- **Method**: `POST`
- **Body**:
```json
{
    "firstName": "name",
    "lastName": "name",
    "birthDate": "1939-12-01",
    "email": "your mail",
    "phoneNumber": "",
    "organization": {
        "id": 4070,
        "name": "Army"
    },
    "dischargeDate": "2025-05-29",
    "locale": "en-US",
    "country": "US",
    "metadata": {
        "marketConsentValue": false,
        "refererUrl": "",
        "verificationId": "",
        "flags": "{\"doc-upload-considerations\":\"default\",\"doc-upload-may24\":\"default\",\"doc-upload-redesign-use-legacy-message-keys\":false,\"docUpload-assertion-checklist\":\"default\",\"include-cvec-field-france-student\":\"not-labeled-optional\",\"org-search-overlay\":\"default\",\"org-selected-display\":\"default\"}",
        "submissionOptIn": "By submitting the personal information above, I acknowledge that my personal information is being collected under the <a target=\"_blank\" rel=\"noopener noreferrer\" class=\"sid-privacy-policy sid-link\" href=\"https://openai.com/policies/privacy-policy/\">privacy policy</a> of the business from which I am seeking a discount, and I understand that my personal information will be shared with SheerID as a processor/third-party service provider in order for SheerID to confirm my eligibility for a special offer. Contact OpenAI Support for further assistance at support@openai.com"
    }
}
```

**Important field notes:**
- `firstName`: given name
- `lastName`: family name
- `birthDate`: date of birth, format `YYYY-MM-DD`
- `email`: email address
- `phoneNumber`: phone number (can be empty)
- `organization`: military organization info (see list below)
- `dischargeDate`: discharge date, format `YYYY-MM-DD`
- `locale`: locale, typically `en-US`
- `country`: country code, typically `US`
- `metadata`: additional metadata (including consent text and flags)

---

## 🎖️ Military Organization List (`organization`)

The following military organizations are available:

```json
[
    {
        "id": 4070,
        "idExtended": "4070",
        "name": "Army",
        "country": "US",
        "type": "MILITARY",
        "latitude": 39.7837304,
        "longitude": -100.445882
    },
    {
        "id": 4073,
        "idExtended": "4073",
        "name": "Air Force",
        "country": "US",
        "type": "MILITARY",
        "latitude": 39.7837304,
        "longitude": -100.445882
    },
    {
        "id": 4072,
        "idExtended": "4072",
        "name": "Navy",
        "country": "US",
        "type": "MILITARY",
        "latitude": 39.7837304,
        "longitude": -100.445882
    },
    {
        "id": 4071,
        "idExtended": "4071",
        "name": "Marine Corps",
        "country": "US",
        "type": "MILITARY",
        "latitude": 39.7837304,
        "longitude": -100.445882
    },
    {
        "id": 4074,
        "idExtended": "4074",
        "name": "Coast Guard",
        "country": "US",
        "type": "MILITARY",
        "latitude": 39.7837304,
        "longitude": -100.445882
    },
    {
        "id": 4544268,
        "idExtended": "4544268",
        "name": "Space Force",
        "country": "US",
        "type": "MILITARY",
        "latitude": 39.7837304,
        "longitude": -100.445882
    }
]
```

**ID mapping:**
- `4070` - Army
- `4073` - Air Force
- `4072` - Navy
- `4071` - Marine Corps
- `4074` - Coast Guard
- `4544268` - Space Force

---

## 🔑 Implementation Notes

1. **Call order is mandatory**  
   You **must** call `collectMilitaryStatus` first, obtain `submissionUrl`, and only then call `collectInactiveMilitaryPersonalInfo`.

2. **Organization info**  
   The `organization` field must contain at least `id` and `name`.  
   You can either randomly select from the list above or allow the user to choose.

3. **Date format**  
   `birthDate` and `dischargeDate` must use the `YYYY-MM-DD` format.

4. **Metadata**  
   The `metadata.submissionOptIn` field contains long privacy/consent text.  
   You should extract it from the original request or reuse it exactly to avoid validation issues.

---

## 📝 To-Do Items

- [ ] Implement the `collectMilitaryStatus` API call
- [ ] Implement the `collectInactiveMilitaryPersonalInfo` API call
- [ ] Add logic to select a military organization
- [ ] Generate realistic personal information (name, birth date, email, etc.)
- [ ] Generate a realistic discharge date (within a reasonable time range)
- [ ] Handle metadata fields (extract from original requests or construct correctly)
- [ ] Integrate this flow into the main bot command system (e.g. `/verify6`)

