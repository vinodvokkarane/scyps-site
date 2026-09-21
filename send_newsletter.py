#!/usr/bin/env python3
"""Send the monthly newsletter from director@smartcyberphysical.org.

    python3 send_newsletter.py 2026-08 --to director    # preview to the director only
    python3 send_newsletter.py 2026-08 --to list        # everyone in recipients.txt

Needs RESEND_API_KEY in the environment (a repository secret on GitHub). The domain must be verified
in Resend first; see README, "Sending the newsletter".

Recipients go in BCC so nobody sees the list. Sends in batches of 45, which is inside Resend's limit
per request. Every message carries a List-Unsubscribe header and a reply-to of the director's UML
address, so replies land somewhere a person reads them.
"""
import json, os, sys, urllib.request, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
FROM = "Center for Smart Cyber-Physical Systems <director@smartcyberphysical.org>"
REPLY_TO = "Vinod_Vokkarane@uml.edu"
DIRECTOR = "Vinod_Vokkarane@uml.edu"
MONTHS = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def recipients():
    """One address per line in recipients.txt; blank lines and lines starting with # are ignored."""
    path = os.path.join(HERE, "recipients.txt")
    if not os.path.exists(path):
        sys.exit("recipients.txt not found")
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if line and "@" in line:
            out.append(line)
    seen, uniq = set(), []
    for a in out:
        if a.lower() not in seen:
            seen.add(a.lower()); uniq.append(a)
    return uniq


def send(to_addrs, subject, html, text, key, bcc=True):
    body = {
        "from": FROM,
        "to": [DIRECTOR] if bcc else to_addrs,
        "reply_to": REPLY_TO,
        "subject": subject,
        "html": html,
        "text": text,
        "headers": {"List-Unsubscribe": f"<mailto:{REPLY_TO}?subject=Unsubscribe>"},
    }
    if bcc:
        body["bcc"] = to_addrs
    req = urllib.request.Request("https://api.resend.com/emails", data=json.dumps(body).encode("utf-8"),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    ym = sys.argv[1]
    mode = sys.argv[sys.argv.index("--to") + 1] if "--to" in sys.argv else "director"
    key = os.environ.get("RESEND_API_KEY", "").strip()
    if not key:
        sys.exit("RESEND_API_KEY is not set")
    html_path = os.path.join(HERE, "newsletters", f"{ym}-email.html")
    txt_path = os.path.join(HERE, "newsletters", f"{ym}.txt")
    if not os.path.exists(html_path):
        sys.exit(f"{html_path} not found; build it first: python3 build_site.py index.html --newsletter={ym}")
    html = open(html_path, encoding="utf-8").read()
    text = open(txt_path, encoding="utf-8").read() if os.path.exists(txt_path) else ""
    label = f"{MONTHS[int(ym[5:7])]} {ym[:4]}"

    if mode == "director":
        r = send([DIRECTOR], f"[Preview] SCyPS newsletter, {label}", html, text, key, bcc=False)
        print(f"preview sent to {DIRECTOR}: {r.get('id')}")
        return

    addrs = recipients()
    if not addrs:
        sys.exit("recipients.txt has no addresses")
    subject = f"SCyPS newsletter, {label}"
    sent = 0
    for i in range(0, len(addrs), 45):
        batch = addrs[i:i + 45]
        r = send(batch, subject, html, text, key, bcc=True)
        sent += len(batch)
        print(f"batch {i // 45 + 1}: {len(batch)} recipients, id {r.get('id')}")
    log = os.path.join(HERE, "newsletters", "sent.log")
    with open(log, "a", encoding="utf-8") as f:
        f.write(f"{datetime.date.today().isoformat()} {ym} sent to {sent} recipients\n")
    print(f"{label}: sent to {sent} recipients")


if __name__ == "__main__":
    main()
