# PROS CLI Training
## Part 1

In this training task, we will be using the click framework to create a basic command that prints your name.

Follow the basic example from click documentation and the other commands in this project to create a command called `hello_world`. Don't forget to include this command in `pros/cli/main.py` like the other commands.
(Hint: `pros/cli/test.py` is a basic example to start from)

When you run `hello_world` in your terminal you should get the output: `my name is {your name}`.
```
$ pros hello_world
my name is ayush
```

Note: There are a few ways to output to the terminal but for this task just use the built in python `print()` function.

As a bonus, save your name in a variable and print it as a formatted string (not required).

## Part 2

Once you have confirmed your new command works, add an argument to specify the day and output it. Again, the click documentation example is helpful.

```
$ pros hello_world --day=tuesday
my name is ayush and today is tuesday
```
