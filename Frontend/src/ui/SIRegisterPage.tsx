import {Form, Link} from "react-router";

export default function SIRegisterPage() {
   	return <div>
		<div className={`w-lg p-2 bg-purple-400 text-black`}>
			<Form>
				<div className={`m-2 flex flex-col`}>
					<label htmlFor="login">Podaj swoją nazwę użytkownika:</label>
					<input type="text" name="login" className={`bg-white`}/>
				</div>
				<div className={`m-2 flex flex-col`}>
					<label htmlFor="login">Podaj adres e-mail:</label>
					<input type="email" name="email" className={`bg-white`}/>
				</div>
				<div className={`m-2 flex flex-col`}>
					<label htmlFor="password">Podaj hasło:</label>
					<input type="password" name="password" className={`bg-white`}/>
				</div>
				<div className={`m-2 flex`}>
					<div>
						<input className={`p-2 cursor-pointer bg-purple-500 text-white underline`} type="submit" value="Zarejestruj się"/>
					</div>
				</div>
			</Form>
		</div>
		<div>
			<Link to="/login">Mam już konto</Link>
		</div>
		<div>
			<Link to="/">Powrót do strony głównej</Link>
		</div>
	</div>
}