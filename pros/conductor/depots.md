# Adding Depots

`pros conduct add-depot --name=<name-of-your-depot> --url=<https://url-for-your-depot>`
`pros conduct add-depot --name <name-of-your-depot> --url <https://url-for-your-depot>`

Example:
```bash
$ pros conduct add-depot --name arms --url "https://github.com/purduesigbots/ARMS/releases/download/v3.1.1/ARMS@3.1.1.zip"
> Added depot arms from https://github.com/purduesigbots/ARMS/releases/download/v3.1.1/ARMS@3.1.1.zip
```

# Removing Depots

`pros conduct remove-depot --name=<name-of-your-depot>`

Example:
```bash 
$ pros conduct remove-depot --name=arms
> Removed depot arms
```


# Query Depots

`pros conduct query-depots --url=True`

`pros conduct query-depots --url=False` (Default)
`pros conduct query-depots`

Examples:
```bash
$ pros conduct query-depots --url True
> arms
>       https://github.com/purduesigbots/ARMS/releases/download/v3.1.1/ARMS@3.1.1.zip
>
> kernel-beta-mainline
>       https://raw.githubusercontent.com/purduesigbots/pros-mainline/master/beta/kernel-beta-mainline.json
>
> pros-mainline
>      https://purduesigbots.github.io/pros-mainline/pros-mainline.json
```
```bash
$ pros conduct query-depots
> arms
>
> kernel-beta-mainline
>
> pros-mainline
```
