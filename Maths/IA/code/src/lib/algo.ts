interface KeycodeSearchInfo {
	firstName: string;
	lastName: string;
	middleName: string;
	email: string;
}


export function KeycodesGenerate(info: KeycodeSearchInfo): string[] {
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

	return [... new Set(results)];
}

console.log(KeycodesGenerate({
	email: 'qit',
	firstName: 'qit',
	lastName: 'qit',
	middleName: 'qit',
}));