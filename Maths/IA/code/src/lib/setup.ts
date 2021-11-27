import fetch from 'node-fetch';

export interface UserCookies {
	'ASP.NET_SessionId': string;
	'.ASPXAUTH': string;
}

export interface UserDetails {
	username: string;
	password: string;
}

const URL = "https://spider.scotscollege.school.nz/Spider2011/Handlers/Login.asmx/GetWebLogin";

export async function cookiesRetrieve(details: UserDetails): Promise<UserCookies> {
    const response = await fetch(URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "UserName": details.username,
            "Password": details.password,
            "SecurityKey": ""
        })
    });

    if (!response.ok || response.status !== 200) {
        throw new Error('failed to get cookies');
    }

    const cookiesText = response.headers.get('set-cookie');
    const cookies: any = Object.fromEntries(
        cookiesText
            .split(' ')
            .filter(pair => pair.includes('ASP.NET_SessionId') || pair.includes('.ASPXAUTH'))
            .map(pair => pair.split('=').map(t => t.trim()))
    );


    return cookies;
}
