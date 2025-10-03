import re
import binascii
import os
from pathlib import Path

def extract_jfif_from_hex(hex_string, output_dir="extracted_images"):
    """
    extract
    
    参数:
        hex_string: 包含JFIF图片的十六进制字符串
        output_dir: 输出目录，默认为"extracted_images"
    
    返回:
        提取的图片数量
    """
    # 创建输出目录
    Path(output_dir).mkdir(exist_ok=True)
    
    # 确保十六进制字符串是连续的（移除空格、换行等）
    hex_string = re.sub(r'\s+', '', hex_string)
    
    # 检查并修复奇数长度的十六进制字符串
    if len(hex_string) % 2 != 0:
        print(f"警告: 十六进制字符串长度为奇数 ({len(hex_string)})，已自动补0")
        hex_string = hex_string + '0'  # 在末尾补0使其成为偶数长度
    
    # 将十六进制字符串转换为字节列表（两个字符一组）
    hex_pairs = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]
    
    # JFIF文件起始标记 (FF D8 FF E0)
    jfif_start = ['ff', 'd8', 'ff', 'e0']
    
    # JPEG文件结束标记 (FF D9)
    jpeg_end = ['ff', 'd9']
    
    extracted_count = 0
    i = 0
    
    # 遍历所有字节对
    while i < len(hex_pairs) - 3:
        # 检查是否匹配JFIF起始标记
        if (hex_pairs[i].lower() == jfif_start[0] and
            hex_pairs[i+1].lower() == jfif_start[1] and
            hex_pairs[i+2].lower() == jfif_start[2] and
            hex_pairs[i+3].lower() == jfif_start[3]):
            
            print(f"找到JFIF起始标记在位置 {i}")
            
            # 从当前位置开始查找结束标记
            j = i
            found_end = False
            
            while j < len(hex_pairs) - 1:
                # 检查是否匹配JPEG结束标记
                if (hex_pairs[j].lower() == jpeg_end[0] and
                    hex_pairs[j+1].lower() == jpeg_end[1]):
                    
                    print(f"找到JPEG结束标记在位置 {j}")
                    found_end = True
                    break
                j += 1
            
            if found_end:
                # 提取从起始标记到结束标记的所有字节对
                jfif_hex_pairs = hex_pairs[i:j+2]  # 包含结束标记
                jfif_hex = ''.join(jfif_hex_pairs)
                
                try:
                    # 将十六进制转换为字节
                    jfif_bytes = binascii.unhexlify(jfif_hex)
                    
                    # 验证文件结构
                    if is_valid_jfif(jfif_bytes):
                        # 保存文件
                        filename = os.path.join(output_dir, f"extracted_image_{extracted_count+1}.jpg")
                        with open(filename, 'wb') as f:
                            f.write(jfif_bytes)
                        
                        print(f"成功提取图片 {extracted_count+1}: {filename} (大小: {len(jfif_bytes)} 字节)")
                        extracted_count += 1
                        
                        # 跳过已提取的图片数据
                        i = j + 2
                    else:
                        print(f"图片 {extracted_count+1} 结构验证失败")
                        i += 1
                        
                except (binascii.Error, ValueError) as e:
                    print(f"图片 {extracted_count+1} 转换失败: {e}")
                    i += 1
            else:
                print("未找到JPEG结束标记")
                i += 1
        else:
            i += 1
    
    print(f"\n总共提取了 {extracted_count} 张图片")
    return extracted_count

def is_valid_jfif(data):
    """
    验证数据是否为有效的JFIF文件
    """
    # 检查起始标记
    if len(data) < 4 or data[:4] != b'\xff\xd8\xff\xe0':
        return False
    
    # 检查结束标记
    if len(data) < 2 or data[-2:] != b'\xff\xd9':
        return False
    
    # 检查JFIF标识符 (在APP0段中)
    if len(data) < 20 or b'JFIF' not in data[6:20]:
        return False
    
    return True

def read_hex_from_file(filename):
    """
    从文件中读取十六进制数据
    """
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"文件 {filename} 不存在")
        return None

# 使用示例
if __name__ == "__main__":
    # 示例1: 从文件读取十六进制数据
    hex_data = read_hex_from_file("hex")
    
    if hex_data:
        extract_jfif_from_hex(hex_data)
    
    # # 示例2: 直接使用十六进制字符串
    # # 这里是一个简化的示例十六进制流，包含一个JFIF图片
    # sample_hex = (
    #     "48656C6C6F20576F726C64"  # 一些无关数据 "Hello World"
    #     "FFD8FFE000104A46494600010100000100010000"  # JFIF开始标记和APP0段
    #     "FFE100184578696600004D4D002A0000000800000000000000"  # 更多图片数据
    #     "FFDB0043000201010201010202020202020202030503030303"  # 量化表
    #     # ... 更多图片数据 ...
    #     "FFD9"  # JPEG结束标记
    #     "7461696C2064617461"  # 更多无关数据 "tail data"
    # )
    
    # 提取示例中的图片
    # extract_jfif_from_hex(sample_hex)