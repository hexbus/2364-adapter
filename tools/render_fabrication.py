"""Render previews from the exact delivery ZIP, including every manufacturing layer."""
import tempfile
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
from fab_geometry import ROOT, NAME, ZIP, primitives, drills

SCALE=40
MARGIN=35
SIZE=(23*SCALE+MARGIN*2,37*SCALE+MARGIN*2)

def xy(x,y):return ((x-48)*SCALE+MARGIN,(-y-48)*SCALE+MARGIN)

def draw_layer(im,items,color):
    d=ImageDraw.Draw(im)
    for p in items:
        kind=type(p).__name__
        if kind=='Circle':
            x,y=xy(p.x,p.y);r=p.r*SCALE
            d.ellipse((x-r,y-r,x+r,y+r),fill=color)
        elif kind=='Rectangle':
            assert p.rotation==0
            x,y=xy(p.x,p.y);w,h=p.w*SCALE/2,p.h*SCALE/2
            d.rectangle((x-w,y-h,x+w,y+h),fill=color)
        elif kind=='Line':
            a,b=xy(p.x1,p.y1),xy(p.x2,p.y2);r=p.width*SCALE/2
            d.line([a,b],fill=color,width=max(1,round(p.width*SCALE)))
            for x,y in (a,b):d.ellipse((x-r,y-r,x+r,y+r),fill=color)
        else:raise AssertionError(kind)

def main():
    dest=ROOT/'docs/images'
    with tempfile.TemporaryDirectory() as tmp,zipfile.ZipFile(ZIP) as z:
        folder=Path(tmp)
        for n in z.namelist():
            assert Path(n).name==n
            (folder/n).write_bytes(z.read(n))
        holes=drills(folder/(NAME+'.drl'))
        for side,cs,ms,ss in [('top','-F_Cu.gtl','-F_Mask.gts','-F_Silkscreen.gto'),('bottom','-B_Cu.gbl','-B_Mask.gbs','-B_Silkscreen.gbo')]:
            im=Image.new('RGB',SIZE,'#f3f4f6')
            d=ImageDraw.Draw(im);d.rectangle((MARGIN,MARGIN,SIZE[0]-MARGIN,SIZE[1]-MARGIN),fill='#14533c')
            draw_layer(im,primitives(folder/(NAME+cs)),'#287756')
            draw_layer(im,primitives(folder/(NAME+ms)),'#d8bb77')
            draw_layer(im,primitives(folder/(NAME+ss)),'#f6f7ef')
            for x,y in holes:
                px,py=xy(x,y);r=.4*SCALE
                ImageDraw.Draw(im).ellipse((px-r,py-r,px+r,py+r),fill='#19231f')
            if side=='bottom':im=ImageOps.mirror(im)
            im.save(dest/(side+'.png'))
        panels=[]
        for suffix,label in [('-F_Cu.gtl','TOP COPPER'),('-B_Cu.gbl','BOTTOM COPPER'),('-F_Mask.gts','TOP MASK OPENINGS'),('-B_Mask.gbs','BOTTOM MASK OPENINGS'),('-F_Silkscreen.gto','TOP SILK'),('-B_Silkscreen.gbo','BOTTOM SILK'),('-Edge_Cuts.gm1','OUTLINE')]:
            im=Image.new('RGB',SIZE,'white')
            draw_layer(im,primitives(folder/(NAME+suffix)),'black')
            im.save(dest/(suffix[1:]+'.png'))
            panels.append((label,im))
        im=Image.new('RGB',SIZE,'white');d=ImageDraw.Draw(im)
        for x,y in holes:
            px,py=xy(x,y);r=.4*SCALE;d.ellipse((px-r,py-r,px+r,py+r),fill='black')
        im.save(dest/'drills.png');panels.append(('PLATED DRILLS: 52 x 0.80 mm',im))
        sheet=Image.new('RGB',(4*360,2*620),'#e8eaed')
        d=ImageDraw.Draw(sheet)
        for i,(label,im) in enumerate(panels):
            im.thumbnail((345,560));x=(i%4)*360;y=(i//4)*620
            d.text((x+10,y+10),label,fill='black');sheet.paste(im,(x+7,y+40))
        sheet.save(dest/'fabrication-layers.png')
    print('Rendered ZIP composites and eight manufacturing-layer previews')

if __name__=='__main__':main()
