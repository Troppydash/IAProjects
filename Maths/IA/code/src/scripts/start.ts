import { cookiesRetrieve } from "../lib/setup";
import {queryAll} from "../lib/query";





async function main(args: string[]): Promise<number> {
	console.log('script started');

	const cookies = await cookiesRetrieve({
		"username": "LI.SCOTS",
		"password": "forqtr0921",
	});

	const result = await queryAll(cookies, 80000, 90000);

	console.log('script ended');
	return 0;
}


main(process.argv.slice(2))
	.then((exitCode) => {
		process.exit(exitCode);
	})
	.catch((err) => {
		console.error(err);
		process.exit(1);
	});
