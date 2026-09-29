import csv, io, os, secrets, time
from datetime import datetime, timezone
from flask import Flask, redirect, request, session, url_for, render_template, jsonify, Response
import requests

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))
CLIENT_ID=os.getenv("REDDIT_CLIENT_ID","")
CLIENT_SECRET=os.getenv("REDDIT_CLIENT_SECRET","")
REDIRECT_URI=os.getenv("REDDIT_REDIRECT_URI","http://localhost:8787/oauth/callback")
USER_AGENT=os.getenv("REDDIT_USER_AGENT","windows:reddit-account-organizer:v0.1.0")
READ_ONLY=os.getenv("READ_ONLY","true").lower() != "false"
AUTH="https://www.reddit.com/api/v1/authorize"
TOKEN="https://www.reddit.com/api/v1/access_token"
API="https://oauth.reddit.com"
SCOPES="identity mysubreddits read subscribe"

def headers(): return {"Authorization":f"bearer {session.get('access_token','')}","User-Agent":USER_AGENT}
def api_get(path, params=None):
    r=requests.get(API+path,headers=headers(),params=params,timeout=30); r.raise_for_status(); return r.json()
def paged(path, params=None):
    out=[]; after=None
    while True:
        p=dict(params or {}); p.update({"limit":100});
        if after: p["after"]=after
        data=api_get(path,p); out += data.get("data",{}).get("children",[])
        after=data.get("data",{}).get("after")
        if not after: return out

def subreddit_stats(name):
    about=api_get(f"/r/{name}/about").get("data",{})
    newest=api_get(f"/r/{name}/new",{"limit":100}).get("data",{}).get("children",[])
    now=time.time(); dates=[x.get("data",{}).get("created_utc",0) for x in newest]
    latest=max(dates) if dates else None
    return {
      "name":name,"subscribers":about.get("subscribers"),"active":about.get("accounts_active"),
      "over18":about.get("over18",False),"created_utc":about.get("created_utc"),
      "latest_post_utc":latest,"days_since_post":round((now-latest)/86400,1) if latest else None,
      "posts_7d":sum(d>=now-7*86400 for d in dates),"posts_30d":sum(d>=now-30*86400 for d in dates),
    }

@app.get("/health")
def health(): return jsonify(ok=True, version="0.1.0")
@app.get("/")
def index(): return render_template("index.html", logged_in=bool(session.get("access_token")), read_only=READ_ONLY)
@app.get("/login")
def login():
    state=secrets.token_urlsafe(24); session["oauth_state"]=state
    q={"client_id":CLIENT_ID,"response_type":"code","state":state,"redirect_uri":REDIRECT_URI,"duration":"temporary","scope":SCOPES}
    return redirect(requests.Request("GET",AUTH,params=q).prepare().url)
@app.get("/oauth/callback")
def callback():
    if request.args.get("state") != session.get("oauth_state"): return "OAuth state mismatch",400
    r=requests.post(TOKEN,auth=(CLIENT_ID,CLIENT_SECRET),data={"grant_type":"authorization_code","code":request.args.get("code"),"redirect_uri":REDIRECT_URI},headers={"User-Agent":USER_AGENT},timeout=30)
    r.raise_for_status(); session["access_token"]=r.json()["access_token"]; return redirect(url_for("index"))
@app.get("/api/me")
def me(): return jsonify(api_get("/api/v1/me"))
@app.get("/api/subscriptions")
def subscriptions():
    children=paged("/subreddits/mine/subscriber")
    return jsonify([{"name":x["data"].get("display_name"),"subscribers":x["data"].get("subscribers"),"over18":x["data"].get("over18",False)} for x in children])
@app.get("/api/custom-feeds")
def custom_feeds():
    # Legacy OAuth multireddit route. Return a clear capability error if Reddit denies it.
    r=requests.get(API+"/api/multi/mine",headers=headers(),timeout=30)
    if r.status_code >= 400: return jsonify(error="Custom Feed access unavailable for this app/account", status=r.status_code), r.status_code
    feeds=[]
    for m in r.json():
        data=m.get("data",m); feeds.append({"name":data.get("display_name"),"path":data.get("path"),"subreddits":[s.get("name") for s in data.get("subreddits",[])]})
    return jsonify(feeds)
@app.get("/api/analyze")
def analyze():
    names=[x["data"].get("display_name") for x in paged("/subreddits/mine/subscriber")]
    rows=[]
    for n in names:
        try: rows.append(subreddit_stats(n))
        except Exception as e: rows.append({"name":n,"error":str(e)})
    return jsonify(rows)
@app.get("/export.csv")
def export_csv():
    names=[x["data"].get("display_name") for x in paged("/subreddits/mine/subscriber")]
    s=io.StringIO(); w=csv.writer(s); w.writerow(["subreddit"]); [w.writerow([n]) for n in names]
    return Response(s.getvalue(),mimetype="text/csv",headers={"Content-Disposition":f"attachment; filename=subscriptions-{datetime.now(timezone.utc).date()}.csv"})
@app.post("/api/unsubscribe")
def unsubscribe():
    if READ_ONLY: return jsonify(error="READ_ONLY is enabled"),403
    names=request.json.get("subreddits",[])
    if not names: return jsonify(error="No subreddits supplied"),400
    r=requests.post(API+"/api/subscribe",headers=headers(),data={"action":"unsub","sr_name":",".join(names)},timeout=30)
    if r.status_code >= 400: return jsonify(error=r.text),r.status_code
    return jsonify(ok=True,count=len(names))
