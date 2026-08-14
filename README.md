# Medical Data Mapping Project (TMT & TMLT to SNOMED-CT)

## Overview
โปรเจกต์นี้มีจุดประสงค์เพื่อสร้างการเชื่อมความสัมพันธ์ (Mapping) ระหว่างฐานข้อมูลทางการแพทย์ของไทย และมาตรฐานสากล โดยเน้นที่ 2 ฐานข้อมูลหลัก:
1. **TMT (Thai Medicines Terminology)** แมปไปยัง **SNOMED-CT**
2. **TMLT (Thai Medical Laboratory Terminology)** แมปไปยัง **SNOMED-CT**

## ข้อมูลที่ใช้ในระบบ (Data Sources)
1. **SNOMED-CT**: ฐานข้อมูลมาตรฐานสากล มีทั้งหมด 6 ไฟล์ในรูปแบบตารางบีบอัด (`.parquet`)
2. **TMT (Thai Medicines Terminology)**:
   - `MasterTMT`: ไฟล์ที่กระจายข้อมูลยาตามรายละเอียด (เช่น ชื่อยา, ตัวยา, หน่วยยา, ขนาดยา เป็นต้น)
   - `Concept` folder: รายการยาตามประเภทของยา (ไฟล์ `.xls` ข้อมูลดิบ / `.json` ข้อมูลที่จัดระเบียบแล้วบางส่วน)
   - `Relationship` folder: รายการเชื่อมโยงภายในระหว่างฐานข้อมูล TMT 
3. **TMLT (Thai Medical Laboratory Terminology)**:
   - `Concept` folder: รายการตามประเภทของการตรวจ (`ITEM` = รายการแยกเดี่ยว, `PANEL` = รายการชุดตรวจ)
   - `Relationship` folder: รายการเชื่อมโยงภายในระหว่างฐานข้อมูล TMLT

---

## ขั้นตอนการทำงานและเป้าหมายการ Mapping (Mapping Guidelines)
การสร้าง Mapping ระหว่างฐานข้อมูล จะทำการแยกประเภทของ SNOMED-CT ออกเป็นหมวดหมู่ต่างๆ เพื่อให้สอดคล้องกับ TMT และ TMLT ดังนี้:

### 1. หมวดหมู่สำหรับ TMT (ยา)
สามารถเชื่อมโยงไปยังหมวดหมู่ของ SNOMED-CT ได้แก่:
- **Substance** (ชื่อสารเคมี)
- **Medicinal Product** (ผลิตภัณฑ์จากสารเคมี)
- **Medicinal Product Form** (ผลิตภัณฑ์จากสารเคมีที่ระบุลักษณะการใช้)
- **Clinical Drug** (ยาที่ใช้จริง)

### 2. หมวดหมู่สำหรับ TMLT (การตรวจทางห้องปฏิบัติการ)
สามารถเชื่อมโยงไปยังหมวดหมู่ของ SNOMED-CT ได้แก่:
- **Procedure** (หัตถการ)
- **Regime/Therapy** (หลักการปฏิบัติ/การบำบัด)

*หมายเหตุ: ในเบื้องต้นระบบจะเริ่มทำการ Mapping จาก 2 กลุ่มใหญ่นี้ เพื่อสร้างเป็น Data Pipeline สำหรับรองรับข้อมูลหมวดอื่นๆ ที่จะเข้ามาในอนาคต*

---

## Protocol การ Mapping กลุ่มข้อมูลยา (Hierarchical Fallback)
เป้าหมายหลักคือการ Map ข้อมูลไปหา SNOMED-CT ในระดับที่ **"ละเอียดที่สุดก่อน"** หากระบบไม่พบข้อมูลที่ตรงกันเป๊ะ จะทำการถอยระดับ (Fallback) ออกมาในกลุ่มที่กว้างขึ้นเรื่อยๆ ตามลำดับดังนี้:
`Clinical Drug -> Medicinal Product Form -> Medicinal Product -> Substance`

### ตัวอย่างการทำงาน (Example)
**ข้อมูลตั้งต้น:** `"BRUSOFT Ibuprofen 400 mg soft gel capsule"`
- **ตัวยา:** Ibuprofen
- **ขนาด:** 400
- **หน่วย:** mg
- **ลักษณะ:** capsule
- **ยี่ห้อ:** BRUSOFT

**ลำดับการ Mapping จะทำงานดังนี้:**

1. **ระดับ Clinical Drug (ละเอียดที่สุด - เป้าหมายแรก)** 
   - *สิ่งที่ระบบพยายามหา:* `Ibuprofen 400 mg oral capsule`
   - *SNOMED-CT Concept:* `1275609004 |Product containing precisely ibuprofen 400 milligram/1 each conventional release oral capsule (clinical drug)|`
   - *(ถ้าไม่พบในระดับนี้ จะถอยไปหาระดับที่ 2)*

2. **ระดับ Medicinal Product Form (ถอยระดับครั้งที่ 1)** 
   - *สิ่งที่ระบบพยายามหา:* `Ibuprofen only product in oral dose form`
   - *SNOMED-CT Concept:* `779527000 |Product containing only ibuprofen in oral dose form (medicinal product form)|`

3. **ระดับ Medicinal Product (ถอยระดับครั้งที่ 2)** 
   - *สิ่งที่ระบบพยายามหา:* `Ibuprofen only product`
   - *SNOMED-CT Concept:* `776287003 |Product containing only ibuprofen (medicinal product)|`

4. **ระดับ Substance (ระดับกว้างที่สุด - เป้าหมายสุดท้าย)** 
   - *สิ่งที่ระบบพยายามหา:* `Ibuprofen`
   - *SNOMED-CT Concept:* `387207008 |Ibuprofen (substance)|`

ด้วย Protocol นี้ จะช่วยแก้ปัญหาในกรณีที่ไม่สามารถหา ขนาด/หน่วยยา แบบ Exact Match ได้ ทำให้มั่นใจได้ว่าข้อมูลยาทุกตัวจะถูก Map ไปยังมาตรฐานสากลได้อย่างถูกต้องและมีตรรกะรองรับเสมอ