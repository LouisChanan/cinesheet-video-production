# พรอมป์ต์ภาษาอังกฤษสำหรับ MiniMax H3 Ref2VA

เขียน Positive Prompt หนึ่งชุดต่อช็อตตามลำดับหกหัวข้อต่อไปนี้ ใช้ชื่อบทบาทเป็นภาษาอังกฤษในร่าง storyboard แล้วแทนด้วยแท็กจริงหลังตรวจ [ตารางจับคู่](sop-analysis.md) ในขั้นตั้งค่า ใช้รูปแบบอื่นเมื่อกราฟที่ตรวจจริงกำหนดไว้

1. **`subject_definitions`** นิยามตัวละคร สถานที่ พร็อพ หรือสินค้าที่ใช้ลักษณะจากภาพด้วย `<Subject N>` แล้วอ้าง `<Picture N>` เป็นแหล่งภาพในบรรทัดเดียว ระบุส่วนที่ใช้จากแผ่นเต็ม เช่น ใบหน้าช่องซ้าย ชุดช่องกลาง หรือฉลากด้านหน้า เขียน `<Picture N>` เป็นรายการแยกเมื่อภาพทำหน้าที่กำหนดเฟรมแรก คีย์เฟรม เฟรมท้าย หรือองค์ประกอบช็อต นิยาม `<Audio N>` เมื่อโหนดรับเสียงจริงและระบุบทบาทที่ต้องการ
2. **`summary`** เริ่มด้วยประเภทงานในวงเล็บเหลี่ยม เช่น `[reference generation]` หรือ `[reference generation + audio reference]` ใช้ `keyframe completion` เมื่อภาพทำหน้าที่เป็นจุดยึดเฟรมจริง ใช้ `audio reuse` เมื่อกราฟต้องคัดลอกสัญญาณเสียง และใช้ `audio reference` เมื่อเสียงให้จังหวะ โทน หรือพื้นผิว การนำเสียงพูดต้นฉบับไปมิกซ์ภายหลังอยู่ในแผนตัดต่อ
3. **`retention_analysis`** เขียนหนึ่งบรรทัดต่อแท็กที่นิยามไว้แยกเป็นรายการ ระบุสิ่งที่ต้องคงหรือเปลี่ยน สำหรับภาพและ Subject ใช้ `fully_preserved`, `partially_preserved`, `attribute_transfer` หรือ `weak_reference` สำหรับเสียงใช้ `fully_copy`, `partially_copy`, `reference` หรือ `weak_reference` ตามบทบาทจริง
4. **`detailed_description`** เปิดด้วยแนวภาพและโทน 1–2 ประโยคก่อน `[Shot 1]` เขียนภาพ แสง ตำแหน่งตัวละคร แอ็กชัน กล้อง และ SFX ตามลำดับ กล่าวถึงป้ายอ้างอิงตรงจุดที่มีผล เขียนการเคลื่อนกล้องเป็นประโยคธรรมชาติ ระบุจังหวะและความเร็วตามจำเป็น สำหรับฉากที่มีรายละเอียดมาก ใช้ 350–500 คำอังกฤษเป็นช่วงอ้างอิงจากคู่มือ MiniMax ให้ความยาวตามเนื้อหาที่จำเป็น ค่าเริ่มต้นคือหนึ่งช็อตต่อรัน ถ้าผู้ใช้ขอหลายช็อตในรันเดียว ให้ `[Shot 1]` เริ่มโดยไม่มี timestamp และระบุเวลาตัดที่เพิ่มขึ้นสำหรับช็อตถัดไป เช่น `[Shot 2] At 00:03.500`
5. **`overall_soundscape`** สรุปเสียงบรรยากาศและเสียงกายภาพที่ต้องการจาก H3 ให้ SFX ตรงจังหวะแอ็กชันใน `detailed_description` เสียงพูดอ้างอิงใช้กำกับเวลาขยับปากเมื่อผู้ใช้ต้องการและกราฟรองรับ ให้ระบุบทบาทในนิยาม สรุป และข้อกำหนดการคงอ้างอิง งดใส่บทพูด เนื้อร้อง หรือแท็ก `<d>...</d>` และระบุให้แทร็ก H3 มีเฉพาะเสียงที่ตกลง
6. **`non_diegetic_music`** บรรยายดนตรีบรรเลงที่ต้องการจาก H3 หรือใส่ `N/A` เมื่อบรีฟไม่ใช้เพลง

ตรวจว่าแท็กที่ใช้ตรงกับลำดับไฟล์ใน [SOP Analysis](sop-analysis.md) และตัดบรรทัดของ input ที่ไม่ใช้ เมื่อเป็น voice-over ภายนอกให้บรรยายภาพตามแผน ใช้การซิงก์ปากเฉพาะช็อตที่ขอและตรวจกราฟแล้ว สำหรับงานไม่เห็นหน้าให้จัดเฟรมเฉพาะมือหรือวัตถุ ใช้ข้อความที่เป็นส่วนหนึ่งของฉากหรือสินค้าตามบรีฟ และสงวนข้อความซ้อนภาพให้กับงานที่ผู้ใช้ขอ

ถ้าต้องซิงก์ปากสองคนในช็อตเดียว ให้จับคู่แท็กเสียงกับ Subject คนละรายการใน `subject_definitions` เช่น `<Audio 1>` กับ `<Subject 1>` และ `<Audio 2>` กับ `<Subject 2>` เมื่อกราฟรับเสียงเดี่ยวสองไฟล์ตามลำดับ ใช้ `reference` สำหรับทั้งสองไฟล์และระบุจังหวะที่ปากขยับพร้อมกันใน `detailed_description` ให้ `overall_soundscape` ระบุเฉพาะบรรยากาศและเอฟเฟกต์ที่ต้องการจาก H3

## ตัวอย่างหนึ่งช็อต

ตัวอย่างนี้ใช้ตัวละครในภาพแรก ฉากในภาพที่สอง สินค้าในภาพที่สาม และเสียงซิงก์ปากหนึ่งไฟล์ แผ่นฉากกับสินค้าช่วยให้รูปลักษณ์คงกัน จึงอ้างภาพไว้ในนิยาม Subject

~~~text
subject_definitions:
<Subject 1> is the presenter whose face and hair follow the left panel of <Picture 1>, with wardrobe and proportions from its center panel.
<Subject 2> is the kitchen in <Picture 2>, following the counter layout and window light of the upper-left panel.
<Subject 3> is the bottle in <Picture 3>, following the silhouette, trigger, and existing label from the front view.
<Audio 1> is the approved speech timing reference for <Subject 1>'s visible mouth movement.

summary:
[reference generation + audio reference] A presenter introduces a bottle in the kitchen, with mouth movement timed to <Audio 1>.

retention_analysis:
<Subject 1>: fully_preserved - Keep the face, hairstyle, wardrobe, and proportions defined above.
<Subject 2>: fully_preserved - Keep the counter layout and direction of window light.
<Subject 3>: fully_preserved - Keep the bottle silhouette, trigger, and label design.
<Audio 1>: reference - Follow its timing for visual lip sync.

detailed_description:
Use a natural commercial style with soft daylight and restrained camera movement.
[Shot 1] In <Subject 2>, frame <Subject 1> at the counter in a medium shot. The presenter lifts <Subject 3> upright and keeps its existing label facing camera. Hold the face in view as the mouth moves to the timing of <Audio 1>. As the presenter sets the bottle down, catch the light tap of its base on the counter. End with a gentle push toward the bottle in clear focus.

overall_soundscape:
Use quiet room tone and one light counter tap. Keep the generated track free of speech and singing.

non_diegetic_music:
N/A
~~~

แหล่งอ้างอิง [คู่มือ MiniMax H3 แบบใช้อ้างอิง](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md) · [คู่มือ MiniMax H3 พื้นฐาน](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md)
