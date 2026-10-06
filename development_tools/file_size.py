# Opens 'output.txt' in write mode with UTF-8 encoding
with open('small_file.txt', 'w', encoding='utf-8') as file:
 # Loops 5 times, from 0 to 4
    for i in range(10):
        line = f"This is line number {i}\n"
        file.write(line)

with open('big_file.txt', 'w', encoding='utf-8') as file:
    for i in range(2000):
        line = f"This is line number {i}\n"
        file.write(line)


