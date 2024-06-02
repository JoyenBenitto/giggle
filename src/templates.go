package  main

//will hold  the template for the nav bar
var site_template = `
{{header}}
{{body}}
{{footer}}
`

var footer = `
	<div>
		<footer className="font-sans mt-auto bg-white dark:bg-background border-t border-white border-opacity-25 m-4 underline-offset-4">
			<div className="w-full max-w-screen-xl mx-auto p-4 md:py-8">
		        <div className="sm:flex sm:items-center sm:justify-between">
		            <a href="/" className="flex items-center mb-4 sm:mb-0">
		                <span className="self-center text-l text-gray-300 text-opacity-75 whitespace-nowrap">Joyen Benitto</span>
		            </a>
		            <ul className="flex flex-wrap items-center mb-6 text-sm font-medium text-gray-500 sm:mb-0 dark:text-gray-400">
		                <li>
		                    <a href="https://github.com/JoyenBenitto" className="mr-4 hover:underline md:mr-6 ">Github</a>
		                </li>
		                <li>
		                    <a href="https://twitter.com/JoyenBenitto" className="mr-4 hover:underline md:mr-6 ">Twitter</a>
		                </li>
		                <li>
		                    <a href="https://www.linkedin.com/in/joyen-benitto-4436031b3/" className="mr-4 hover:underline md:mr-6 ">Linkedin</a>
		                </li>
		                <li>
		                    <a href="/contacts" className="hover:underline">Contact</a>
		                </li>

		            </ul>
		        </div>
		        <hr className="my-6 border-gray-200 sm:mx-auto dark:border-gray-700 lg:my-8" />
		        <span className="block text-sm text-gray-500 sm:text-center dark:text-gray-400">© 2024 <a href="/" className="hover:underline text-button_pink hover:text-opacity-100">Joyen Benitto</a>. All Rights Reserved.</span>
		    </div>
		</footer>
	</div>
`