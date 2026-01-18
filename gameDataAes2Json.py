from Crypto.Cipher import AES

def rizline_aes_decrypt(encrypt_data: bytes, key: bytes = b"Sv@H,+SV-U*VEjCW,n7WA-@n}j3;U;XF", iv: bytes = b"1%[OB.<YSw?)o:rQ") -> str | None:
    """
    Rizline 专属AES-CBC解密函数
    :param encrypt_data: 待解密的二进制数据 (bytes类型)
    :param key: 解密密钥 (bytes类型)
    :param iv: 解密向量 (bytes类型)
    :return: 解密成功返回字符串内容，失败返回None
    """
    try:
        # 1. 初始化AES CBC解密器并执行解密
        cipher = AES.new(key, AES.MODE_CBC, iv)
        dec_data = cipher.decrypt(encrypt_data)
        
        # 2. 应用 Rizline 特有的填充裁剪核心逻辑: ~last_byte & 0xFF
        last_byte = dec_data[-1]
        pad_len = (~last_byte) & 0xFF
        
        # 3. 合规填充长度校验（AES分组固定16位，填充长度必须 1~16 才有效）
        if 0 < pad_len <= 16:
            real_data = dec_data[:-pad_len]
        else:
            real_data = dec_data
        
        # 4. UTF-8解码返回明文
        return real_data.decode('utf-8')
    
    except Exception as e:
        print(f"解密失败: {str(e)}")
        return None

# # -------------------------- 调用示例 --------------------------
# if __name__ == "__main__":
#     # 固定密钥和向量（你的原始配置）
#     key_net = b"Sv@H,+SV-U*VEjCW,n7WA-@n}j3;U;XF"
#     iv_net = b"1%[OB.<YSw?)o:rQ"
    
#     # 读取加密文件并解密
#     with open("f:/reverse/body_binary", "rb") as f:
#         encrypt_bytes = f.read()
    
#     # 核心调用：传入【加密二进制内容+密钥+向量】，返回解密文本
#     decrypt_content = rizline_aes_decrypt(encrypt_bytes, key_net, iv_net)
    
#     # 结果处理 & 保存
#     if decrypt_content:
#         print("✅ 解密成功！")
#         print("\n--- 数据预览(前1000字符) ---")
#         print(decrypt_content[:1000] + ("..." if len(decrypt_content) > 1000 else ""))
        
#         with open("f:/reverse/body_decrypted.json", "w", encoding="utf-8") as f:
#             f.write(decrypt_content)
#         print(f"\n📄 完整数据已保存至文件，总长度: {len(decrypt_content)} 字符")
#     else:
#         print("❌ 解密失败，请检查密钥/向量/加密文件是否正确")