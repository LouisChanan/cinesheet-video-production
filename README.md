# CineSheet

CineSheet ช่วยเปลี่ยนบรีฟวิดีโอเป็นแผนที่มีบทพูด สตอรีบอร์ด แผนเสียง และ prompt รายฉาก ข้อมูลหลักอยู่ใน `production.json` เวอร์ชัน `1.0.0` และส่งออกเป็น HTML หรือ Markdown สำหรับรีวิวได้

## ตำแหน่งของ Skill

ไฟล์ [SKILL.md](SKILL.md) ที่ราก repo เป็นคำสั่งต้นฉบับ ให้แก้ไฟล์ใน repo เมื่อพัฒนา Skill แล้วคัดลอกเวอร์ชันที่ต้องการใช้ไปไว้ใน `~/.agents/skills/cinesheet-video-production/` ของแต่ละเครื่อง [วิธีติดตั้งบน Windows](INSTALL_WINDOWS.md)

บน macOS หรือ Linux ให้รันจากราก repo เพื่อคัดลอก Skill สำหรับผู้ใช้ปัจจุบัน

```sh
mkdir -p "$HOME/.agents/skills/cinesheet-video-production"
cp -R SKILL.md adapters agents examples modules references schemas scripts templates requirements.txt "$HOME/.agents/skills/cinesheet-video-production/"
```

จากนั้นเรียก `$cinesheet-video-production` ใน Codex พร้อมบรีฟ ตัวอย่างเช่น `วางแผนคลิปแนวตั้ง 30 วินาที ใช้ MiniMax H3 บทพูดภาษาไทย`

## ลองเปิดเอกสารตัวอย่าง

ใช้ Python 3.10 ขึ้นไป รันจากราก repo หรือโฟลเดอร์ Skill ที่คัดลอกมา

```sh
python3 -m pip install -r requirements.txt
python3 scripts/validate_production.py examples/naturgenic-ugc.json
python3 scripts/render_sheet.py examples/naturgenic-ugc.json --out output/naturgenic/production-sheet.html
python3 scripts/render_sheet.py examples/naturgenic-ugc.json --out output/naturgenic/production-sheet.md --format markdown
```

เปิด `output/naturgenic/production-sheet.html` ในเบราว์เซอร์ ตัวอย่างตั้งใจเว้นไฟล์ภาพสินค้าไว้และระบุข้อกล่าวอ้างที่ยังไม่มีหลักฐาน จึงมีคำเตือนเมื่อ validate

## เริ่มโปรเจกต์ใหม่

```sh
python3 scripts/new_project.py --id my-video-001 --title "My video" --out output/my-video-001
```

เติมบรีฟและฉากอย่างน้อยหนึ่งฉากใน `output/my-video-001/production.json` แล้วรันตัวตรวจและตัวส่งออกด้วยพาธของโปรเจกต์นี้ ไฟล์อ้างอิงที่เก็บเป็นพาธสัมพัทธ์ให้นับจากโฟลเดอร์ JSON ส่วนลิงก์ในเอกสารจะนับจากโฟลเดอร์ที่ส่งออก

เมื่อมีเครื่องมือที่ใช้ได้ ให้ส่ง contact sheet และ character sheet ฉบับร่างพร้อมแผน ผู้ใช้อนุมัติแผนข้อความได้เมื่อภาพยังไม่พร้อม การสร้างภาพเต็มแยกตาม panel และการผลิตวิดีโอใช้การอนุมัติแยกกัน [กติกาอนุมัติ](SKILL.md#approval-gates)

## ตรวจการแก้ไข

```sh
python3 -B scripts/test_skill.py
git diff --check
```
