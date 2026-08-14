import pandas as pd

df = pd.DataFrame({"A": [1, 2, 3]})
df.to_parquet("test.parquet")  # บันทึกไฟล์ Parquet ทดสอบ
df_read = pd.read_parquet("test.parquet")  # ลองอ่านไฟล์
print(df_read)


