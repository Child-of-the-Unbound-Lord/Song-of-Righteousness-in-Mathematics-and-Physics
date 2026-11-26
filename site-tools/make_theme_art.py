#!/usr/bin/env python3
"""Create original vector night scenes for the three secondary character-inspired themes."""
from __future__ import annotations
import random
from io import BytesIO
from pathlib import Path
import cairosvg
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/assets/themes'
OUT.mkdir(parents=True,exist_ok=True)

BASE='''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="900" viewBox="0 0 1280 900">
<defs>
 <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop stop-color="{sky}"/><stop offset="0.56" stop-color="{mid}"/><stop offset="1" stop-color="{floor}"/></linearGradient>
 <radialGradient id="haze"><stop stop-color="{accent}" stop-opacity=".50"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
 <radialGradient id="moon"><stop stop-color="#ffffff"/><stop offset=".8" stop-color="{moon}"/><stop offset="1" stop-color="{accent}"/></radialGradient>
 <filter id="blur"><feGaussianBlur stdDeviation="16"/></filter>
 <filter id="glow"><feGaussianBlur stdDeviation="3"/></filter>
 <linearGradient id="dress" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{dress1}"/><stop offset="1" stop-color="{dress2}"/></linearGradient>
</defs>
<rect width="1280" height="900" fill="url(#sky)"/>
<ellipse cx="770" cy="270" rx="520" ry="350" fill="url(#haze)"/>
{background}
<circle cx="860" cy="200" r="110" fill="{accent}" opacity=".22" filter="url(#blur)"/>
<circle cx="860" cy="185" r="74" fill="url(#moon)" opacity=".88"/>
{stars}
{landscape}
{figure}
{foreground}
<rect x="14" y="14" width="1252" height="872" rx="22" fill="none" stroke="{accent}" stroke-opacity=".18" stroke-width="1"/>
</svg>'''

def starfield(seed, color='#ffffff', qty=92, ymax=550):
    rand=random.Random(seed)
    return ''.join(f'<circle cx="{rand.randint(25,1250)}" cy="{rand.randint(15,ymax)}" r="{rand.choice((1,1,1,2,2,3))}" fill="{color}" opacity="{rand.uniform(.25,.8):.2f}"/>' for _ in range(qty))

def paint(name, colors, background, landscape, figure, foreground, seed):
    svg=BASE.format(**colors,background=background,landscape=landscape,figure=figure,foreground=foreground,stars=starfield(seed))
    (OUT/f'{name}.svg').write_text(svg,encoding='utf-8')
    img=Image.open(BytesIO(cairosvg.svg2png(bytestring=svg.encode('utf-8')))).convert('RGB')
    img.save(OUT/f'{name}.webp', 'WEBP',quality=86,method=6)
    print(name,'saved', (OUT/f'{name}.webp').stat().st_size)

# Snow-blue scholastic windows, long midnight-blue hair and a seated reading silhouette.
paint('yukino',dict(sky='#0a1b37',mid='#234a68',floor='#0b1a2c',accent='#93d9eb',moon='#eefaff',dress1='#0c2640',dress2='#2c4b65'),
 background='''<path d="M0 590V0h115L142 790H0ZM1190 0h90v900h-91Z" fill="#0b1729" opacity=".78"/><path d="M160 0v690M570 0v650M980 0v700M110 390h1080" stroke="#203b58" stroke-width="20" opacity=".8"/><path d="M0 630h1280" stroke="#b5e7f7" stroke-opacity=".15" stroke-width="6"/>''',
 landscape='''<path d="M0 605 135 515 205 560 308 465 448 593 550 510 670 600 785 570 925 610 1065 495 1280 560V900H0Z" fill="#b6e8f8" opacity=".1"/><path d="M0 700 124 645 260 682 365 620 515 698 660 640 810 690 932 648 1082 705 1280 630V900H0Z" fill="#102b48"/><rect x="0" y="740" width="1280" height="160" fill="#0b162a"/><rect x="115" y="695" width="470" height="26" rx="7" fill="#142940"/><rect x="145" y="724" width="33" height="130" fill="#13243b"/><path d="M180 687h360" stroke="#c6e9f0" opacity=".3" stroke-width="3"/><path d="M25 680h290M30 668h285" stroke="#5b8199" stroke-width="9" opacity=".3"/>''',
 figure='''<path d="M735 385Q760 290 840 300Q928 298 943 407L981 760Q885 810 745 740Z" fill="#0e1b39"/><path d="M748 377Q734 266 842 251Q948 251 942 369Q931 427 886 470L877 635Q829 665 756 635Z" fill="#111e3c"/><path d="M774 343Q794 280 855 291Q908 300 917 350L907 436Q861 478 804 436Z" fill="#d8dfe9"/><path d="M788 345Q792 276 857 274Q932 275 931 348Q894 335 860 304Q835 342 788 345Z" fill="#192a4d"/><path d="M748 406Q735 497 717 670L754 790 974 790Q952 534 913 425L861 485Z" fill="url(#dress)"/><path d="M799 479Q848 510 889 481" stroke="#b8d2e2" stroke-width="6" fill="none"/><path d="M816 510L852 575 891 509" stroke="#a3d0ea" stroke-width="3" fill="none"/><path d="M782 367q-52 136-50 315" stroke="#192a4d" stroke-width="18" fill="none"/><path d="M907 369q47 105 38 345" stroke="#152b51" stroke-width="22" fill="none"/><path d="M850 431q11 10 20 0" stroke="#5c6882" stroke-width="2" fill="none"/><path d="M882 400q6-4 13 0" stroke="#25334d" stroke-width="3"/>''',
 foreground='''<path d="M635 680q72-25 154 2l-8 44q-90-23-157 1Z" fill="#c5d5df"/><path d="M655 680q54-7 110 8" stroke="#2c5271" stroke-width="4"/><g fill="#eef9ff" opacity=".68">'''+''.join(f'<circle cx="{random.Random(i).randint(20,1260)}" cy="{random.Random(i*19).randint(40,760)}" r="{random.Random(i*7).choice((2,3,4))}"/>' for i in range(55))+'''</g>''',seed=12)

# Green forest observatory, a wandering silver-haired elven scholar from behind.
paint('frieren',dict(sky='#071b25',mid='#285145',floor='#102a24',accent='#9bd9aa',moon='#fff6da',dress1='#d0d7c9',dress2='#688b81'),
 background='''<path d="M70 700V80l40-26 38 12v626M155 685V0h33v678M1090 666V0h30v690M1128 692V65l36-24 36 28v650" stroke="#142923" stroke-width="48" opacity=".82"/><path d="M50 320q180-200 345-44M960 220q170-150 275 24" stroke="#285745" stroke-width="60" fill="none" opacity=".52"/>''',
 landscape='''<path d="M0 620Q240 460 430 580T860 560T1280 600V900H0Z" fill="#315b45" opacity=".45"/><path d="M0 655Q260 570 490 650T910 660T1280 600V900H0Z" fill="#142f28"/><path d="M225 705V420q8-55 58-61h62q52 12 55 65v281" stroke="#69816d" stroke-width="40" opacity=".6" fill="none"/><path d="M186 705h257v24H186Z" fill="#435d50"/><path d="M160 730h345v35H160Z" fill="#395145"/><path d="M0 770h1280v130H0Z" fill="#0c211f"/>''',
 figure='''<path d="M728 410Q715 318 805 265Q886 228 947 320L995 705Q921 756 745 731Z" fill="#d5ded4"/><path d="M775 353Q758 285 842 272Q931 262 933 349L899 442Q855 462 801 422Z" fill="#ece2ca"/><path d="M780 338Q781 257 858 254Q926 254 935 329L901 300Q875 332 780 338Z" fill="#e9ece8"/><path d="M776 356 713 323 757 376ZM926 351l69-24-57 56Z" fill="#e8dfcd"/><path d="M807 427Q786 535 761 690Q839 758 975 691L916 428 869 480Z" fill="url(#dress)"/><path d="M834 476q26 25 52 0" stroke="#b69f6d" stroke-width="7" fill="none"/><path d="M742 338q-32 160 0 344" stroke="#f5efda" stroke-width="28" fill="none"/><path d="M949 342q32 158 17 358" stroke="#eff5e6" stroke-width="31" fill="none"/><path d="M804 446q-58 46-75 127" stroke="#e3dcc8" stroke-width="19" fill="none"/><path d="M915 449q63 58 73 136" stroke="#d5decf" stroke-width="19" fill="none"/><path d="M842 400q12 4 22 0" stroke="#3b6553" stroke-width="3" fill="none"/>''',
 foreground='''<path d="M0 760Q230 720 480 765T960 766T1280 752V900H0Z" fill="#0c211e"/><g fill="#d7eab6">'''+''.join(f'<circle cx="{random.Random(i+40).randint(12,1268)}" cy="{random.Random(i*23+7).randint(95,780)}" r="{random.Random(i*33+9).choice((2,3,5))}" opacity=".6"/>' for i in range(46))+'''</g><path d="M30 890q80-200 145-130M1220 900q-25-180-130-170" stroke="#5d9670" stroke-width="13" fill="none"/>''',seed=35)

# Warm, curious brown-haired student in a library with open books and brass lamps.
paint('eru',dict(sky='#2a152b',mid='#5a3945',floor='#1f1425',accent='#ebba87',moon='#ffeed2',dress1='#362739',dress2='#7e5360'),
 background='''<path d="M0 0h255v735H0ZM1020 0h260v735h-260Z" fill="#28192b"/><path d="M0 90h270M0 290h270M0 490h270M1010 90h270M1010 290h270M1010 490h270" stroke="#7f5260" stroke-width="13" opacity=".7"/><g fill="#996e60" opacity=".65">'''+''.join(f'<rect x="{30+(i%6)*36}" y="{115+(i//6)*200}" width="{24+(i%3)*4}" height="136" rx="3"/>' for i in range(18))+''.join(f'<rect x="{1048+(i%5)*39}" y="{115+(i//5)*200}" width="{24+(i%2)*7}" height="134" rx="3"/>' for i in range(15))+'''</g><path d="M265 0v730M1014 0v730" stroke="#9f6b65" opacity=".58" stroke-width="14"/>''',
 landscape='''<path d="M0 730H1280V900H0Z" fill="#261726"/><path d="M0 716H1280v30H0Z" fill="#654450"/><rect x="105" y="690" width="560" height="25" rx="7" fill="#876367"/><path d="M115 717v166M625 717v166" stroke="#5d3c45" stroke-width="26"/><path d="M130 688v-160" stroke="#cba478" stroke-width="8"/><path d="M94 536q41-74 83 0Z" fill="#ffd5a0" opacity=".87"/><ellipse cx="134" cy="524" rx="57" ry="44" fill="#fdb66e" opacity=".22" filter="url(#blur)"/>''',
 figure='''<path d="M741 390Q728 262 830 252Q951 238 960 380L992 721Q898 782 746 718Z" fill="#342136"/><path d="M774 349Q783 283 863 279Q943 282 945 370L919 444Q860 481 809 427Z" fill="#f5d5c0"/><path d="M770 337Q755 254 849 238Q951 221 961 326Q928 312 898 285Q836 334 770 337Z" fill="#321b32"/><path d="M771 348q-62 190-40 336" stroke="#311e32" stroke-width="43" fill="none"/><path d="M934 346q62 156 38 337" stroke="#392135" stroke-width="46" fill="none"/><path d="M783 427Q751 489 730 704L759 783H1002Q1009 547 920 420L864 471Z" fill="url(#dress)"/><path d="M815 448q56 22 87 0" fill="none" stroke="#e0b4a9" stroke-width="4"/><path d="M821 490l45 50 43-54" fill="none" stroke="#dfac85" stroke-width="3"/><path d="M843 398q6-6 15 0M892 398q9-6 17 0" stroke="#2f242d" stroke-width="3"/><path d="M865 432q10 7 20-1" stroke="#bb806f" stroke-width="2" fill="none"/>''',
 foreground='''<path d="M405 682l132-40 135 28-137 47Z" fill="#ead1a2"/><path d="M535 718l135-45 21 73-137 33Z" fill="#a97c67"/><path d="M405 682l134 35 15 62-151-22Z" fill="#f8dfbd"/><path d="M537 641q17 40-2 76" stroke="#d8a987" stroke-width="3" fill="none"/><g fill="#f9daa4">'''+''.join(f'<circle cx="{random.Random(i+73).randint(270,1010)}" cy="{random.Random(i*15+4).randint(100,740)}" r="{random.Random(i*10+8).choice((1,2,3))}" opacity=".7"/>' for i in range(36))+'''</g>''',seed=82)

# ImageGen produced the default Mai scene. Resize it once and keep the original
# outside the published asset directory for efficient mobile downloads.
img=Image.open(OUT/'mai-original.png').convert('RGB')
img=ImageOps.fit(img,(1280,900),method=Image.Resampling.LANCZOS,centering=(.58,.5))
img.save(OUT/'mai.webp','WEBP',quality=83,method=6)
(OUT/'mai-original.png').unlink(missing_ok=True)
print('mai saved',(OUT/'mai.webp').stat().st_size)
