# 🌐 Bluesky Survey Bot

Automated Posting System for Academic Research Outreach

The **Bluesky Survey Bot** is a lightweight automation tool designed to help academic teams share their research surveys consistently across social media. It automatically posts SEO-optimized messages, rotates templates and hashtags, and supports fully scheduled publishing. Ideal for research groups looking to increase visibility and reach relevant audiences without manual effort.

---

## ✨ Features

### 🤖 Automated Survey Posting

- Posts directly to **Bluesky** using official API credentials
- Generates messages dynamically using templates
- Automatically inserts your survey link and call-to-action
- Supports **multi-post mode** for broader daily outreach

### 🔁 Smart Variation System

- Rotates between multiple content templates
- Uses dynamic, SEO-optimized hashtag sets
- Ensures every post looks fresh (avoids repetition)

### 📝 Template-Based Content

All post variants are stored in `/templates/post.txt`.  
Simply edit this file to update or add new message structures.

### 📊 Logging & Tracking

- Logs every post into `/logs/`
- Saves post timestamps, preview text, and Bluesky URIs
- Ready for weekly reporting extensions

### 📅 Fully Scheduler-Ready

Integrates easily with Linux `cron` for daily or hourly posting.  
Perfect for deployment on university or research servers.

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/bluesky-survey-bot.git
cd bluesky-survey-bot
```
