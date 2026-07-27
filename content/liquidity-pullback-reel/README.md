# ريل «القاع القوي — وين تحط ستوبك»

درس مفرد لحساب Liquidity State عن سحب السيولة ومكان الستوب.
أُنتِج عبر بايبلاين `production-run` (9 مراحل). البوابة عدّت **15/15** ونطاق التخطي المتوقع **<30%**.

## الملفات
| الملف | الوصف | المرحلة |
|---|---|---|
| `script.md` | السكربت المدموج (VO + شوت بلوكس) بصوت فهد | 3–4 |
| `script.spec.json` | السبيك المعتمد + بلوك التدقيق (skip-risk 15/15) | 5 (البوابة) |
| `vo_manifest.json` | 10 مقاطع فويس أوفر، كل مقطع بميزانية زمنية | 6 |
| `build/remotion.props.json` | 10 مشاهد frame-accurate للرِندر | 7 |
| `build/sfx_cues.json` | 13 كيو صوتي (sub-drop / ticks / risers) | 7 |
| `build/captions.srt` | الكابشن العربي (يُعاد تشكيله قبل الحرق) | 7 |
| `publish.md` | الكابشن + الكوفر + ManyChat + الهاشتاقات + خطة التشخيص | 8–9 |
| `preview.html` | معاينة صامتة تشتغل بالمتصفح (شموع تعليمية) | — |

## ليش ما انرندر MP4 نهائي هني
البيئة تنقصها ثلاثة أشياء إلزامية لريل موثوق:
1. **مفتاح TTS** (ElevenLabs / Azure ar-KW) — بدونه ما فيه فويس أوفر كويتي، والبايبلاين يمنع ريل بدون صوت.
2. **خطوط عربية** (Tajawal) للحرق الصحيح.
3. **شارت XAUUSD 15m حقيقي** من TradingView (المعاينة تستخدم شموع تعليمية تخطيطية).

## خطوات الرِندر النهائي (لما يتوفر مفتاح الصوت)
```bash
export ELEVENLABS_API_KEY=sk_...        # أو AZURE_SPEECH_KEY
cd content/liquidity-pullback-reel

# 1) فويس أوفر — مقطع لكل بيت، ماستر على -14 LUFS
#    (كل clip في vo_manifest.json لازم يكون داخل budget_s؛ إذا تعدّى → قصّر السطر، لا تسرّع فوق 1.15×)
python3 vo/make_vo.py vo_manifest.json -o vo/

# 2) شارت حقيقي: صدّر XAUUSD 15m من TradingView يبيّن
#    هاي قديم مكسور + قاع قوي (بعد الكسر) + قاع ضعيف يُسحب، وحطه bg للمشاهد

# 3) رِندر Remotion من remotion.props.json (الخطوط inline base64، العربي مُعاد تشكيله)
#    ثم مكس الصوت + SFX عبر ffmpeg (متوفر: /opt/pw-browsers/ffmpeg-1011)
#    تحقّق من loop seam: قارن الفريم الأول بالأخير للملف المُصدَّر

# الناتج: reel-1080x1920-30fps.mp4
```

## إعادة التحقق بعد أي تعديل على السكربت
```bash
cd /root/.claude/skills/script-spec-bridge/scripts
python3 parse_script.py    <repo>/content/liquidity-pullback-reel/script.md -o .../script.spec.json
python3 validate_spec.py   .../script.spec.json --write     # لازم يرجع exit 0 و ≥13/15
```
