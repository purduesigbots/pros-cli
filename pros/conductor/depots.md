# Adding Depots

`pros conduct add-depot <name-of-your-depot> <https://url-for-your-depot>`

Example:
```bash
$ pros conduct add-depot test "https://pros.cs.purdue.edu/v5/_static/beta/testing-mainline.json"
> Added depot test from https://pros.cs.purdue.edu/v5/_static/beta/testing-mainline.json
```

# Removing Depots

`pros conduct remove-depot <name-of-your-depot>`

Example:
```bash 
$ pros conduct remove-depot test
> Removed depot test
```


# Query Depots

`pros conduct query-depots --url`
`pros conduct query-depots`

Examples:
```bash
$ pros conduct query-depots --url
> Available Depots:
> 
> kernel-beta-mainline -- https://raw.githubusercontent.com/purduesigbots/pros-mainline/master/beta/kernel-beta-mainline.json
> pros-mainline -- https://purduesigbots.github.io/pros-mainline/pros-mainline.json
> test -- https://pros.cs.purdue.edu/v5/_static/beta/testing-mainline.json
> 
```
```bash
$ pros conduct query-depots
> Available Depots (Add --url for the url):
>
> kernel-beta-mainline
> pros-mainline
> test
> 
```
