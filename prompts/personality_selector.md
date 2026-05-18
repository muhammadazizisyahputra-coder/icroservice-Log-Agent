# 人格选择器（Personality Selector）

## 目标
用以判断对话时激活哪个人格。返回人格 key（例如 normal/angry/drunk）。

## 基本规则示例
1. 优先检测明确修饰词（例如：“你怎么这么生气”，“真讨厌” → angry）
2. 检测情绪强度（感叹号、短句、反复指责 → 偏向 angry）
3. 检测亲密/撒娇关键词（“想你”、“抱抱” → normal）
4. 含酒精/醉酒场景（“喝醉了”、“醉了”）→ drunk
5. 未命中：fallback to normal

## 输出示例
```
选择结果格式：
{
  "selected_personality": "angry",
  "reason": "包含关键词 '生气'，且有短句/感叹号"
}
```
