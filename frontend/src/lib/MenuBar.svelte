<script lang="ts">

let path: string
let logo: string

logo = "/img/EV_Logo_2022.png"
// you cant just reference it directly, because the static renderer will mistake it as a path

</script>
<div class="bg-gray-100 dark:bg-gray-800 sm:h-screen p-2 sm:p-0 sticky top-0">
    <div id="menu" class="flex flex-row sm:h-full sm:flex-col self-start space-x-2 sm:space-y-3 sm:mx-6 sm:pt-4">

        <img src={logo} class=" rounded-md w-10 sm:w-40" alt="team">
        <div class="font-bold w-10 sm:w-auto text-black dark:text-white my-auto">Team 7393</div>

        <div class="flex sm:flex-col flex-row space-x-3 w-full mx-0">
            <a class="transition flex flex-row items-center grow items-center px-2 sm:px-4 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md" href="/logout">
                <div class="font-bold w-full flex-grow py-2 sm:p-0 text-xl sm:text-2xl">
                    logout
                </div>
            </a>
            <a class="transition flex flex-row items-center grow items-center px-2 sm:px-4 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md" href="https://ftc7393.org">
                <div class="font-bold w-full flex-grow py-2 sm:p-0 text-xl sm:text-2xl">
                    ftc7393.org
                </div>
            </a>
            <a class="transition flex flex-row items-center grow items-center px-2 sm:px-4 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md" target="_blank" href="https://github.com/fTC7393/sussy-factory">
                <div class="font-bold w-full flex-grow py-2 sm:p-0 text-xl sm:text-2xl">
                    source
                </div>
            </a>
        </div>

    </div>
</div>

