//const address = (await window.ethereum.request({ method: 'eth_requestAccounts' }))[0]

async function login () {
    await window.ethereum.request({ method: 'eth_requestAccounts' })
    window.web3 = new Web3(window.ethereum)

    fetch('https://www.learnwithjason.dev/graphql', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: `
                query GetLearnWithJasonEpisodes($now: DateTime!) {
                    allEpisode(limit: 10, sort: {date: ASC}, where: {date: {gte: $now}}) {
                        date
                        title
                        guest {
                            name
                            twitter
                        }
                        description
                    }
                }
                `,
            variables: {
                now: new Date().toISOString(),
            },
        }),
    })
    .then((res) => res.json())
    .then((result) => console.log(result));
}

window.addEventListener('load', async function () {
    document.getElementsByClassName('authentication__authenticate')[0].onclick = login
})
