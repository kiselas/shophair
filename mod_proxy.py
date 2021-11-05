new_proxy_list = []
with open('proxy_list.txt') as f:
    content = f.readlines()
    for line in content:
        new_proxy_list.append('http://' + line)

with open('proxy_list_new.txt', 'w') as f:
    for element in new_proxy_list:
         f.write(element)