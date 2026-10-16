"""Vector drawing primitives; copied into each independent project generator."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, FancyArrowPatch

plt.rcParams.update({'font.family':'STIXGeneral', 'mathtext.fontset':'stix',
                     'font.size':9, 'pdf.fonttype':42, 'ps.fonttype':42,
                     'text.usetex':False, 'axes.unicode_minus':False})
CM = 1 / 2.54

class Drawing:
    def __init__(self, bounds):
        x0,y0,x1,y1 = bounds
        self.fig = plt.figure(figsize=((x1-x0)*CM,(y1-y0)*CM))
        self.ax = self.fig.add_axes([0,0,1,1], xlim=(x0,x1), ylim=(y0,y1))
        self.ax.set_aspect('equal'); self.ax.axis('off')
        self.nodes = {}
        self.labels = []

    def text(self,x,y,label,size=9,ha='center',va='center'):
        artist=self.ax.text(x,y,label,fontsize=size,ha=ha,va=va,
                            linespacing=1.15,clip_on=False,zorder=4)
        self.labels.append([artist,None])
        return artist

    def box(self,name,x,y,w,h,label,dashed=False,shape='rect',size=9):
        style = {'edgecolor':'black','facecolor':'white','linewidth':.55,
                 'linestyle':(0,(4,3)) if dashed else 'solid', 'zorder':2}
        if shape == 'diamond':
            obj = Polygon([(x-w/2,y),(x,y+h/2),(x+w/2,y),(x,y-h/2)],**style)
        elif shape == 'circle': obj = Circle((x,y),w/2,**style)
        else: obj = Rectangle((x-w/2,y-h/2),w,h,**style)
        self.ax.add_patch(obj); self.text(x,y,label,size)
        self.labels[-1][1]=(x-w/2,y-h/2,x+w/2,y+h/2)
        self.nodes[name] = (x,y,w,h,shape)

    def point(self,name,side):
        x,y,w,h,_ = self.nodes[name]
        return {'n':(x,y+h/2),'s':(x,y-h/2),'e':(x+w/2,y),
                'w':(x-w/2,y),'nw':(x-w/2,y+h/2),
                'ne':(x+w/2,y+h/2),'c':(x,y)}[side]

    def line(self,points,dashed=False):
        xs,ys=zip(*points)
        self.ax.plot(xs,ys,color='black',linewidth=.55,
                     linestyle=(0,(4,3)) if dashed else 'solid',zorder=1)

    def arrow(self,p,q,dashed=False,via=()):
        points=[p,*via,q]
        if via:self.line(points[:-1],dashed)
        self.ax.add_patch(FancyArrowPatch(points[-2],points[-1],
                         arrowstyle='-|>',mutation_scale=7.5,linewidth=.55,
                         color='black',shrinkA=0,shrinkB=0,
                         linestyle=(0,(4,3)) if dashed else 'solid',zorder=1))

    def edge(self,a,b,sa='s',sb='n',**kwargs):
        self.arrow(self.point(a,sa),self.point(b,sb),**kwargs)

    def frame(self,x,y,w,h):
        self.ax.add_patch(Rectangle((x,y),w,h,fill=False,edgecolor='black',
                                   linewidth=.55,linestyle=(0,(4,3)),zorder=0))

    def save(self,out,name):
        # Fixed physical canvas: do not enlarge or rasterize the scientific figure.
        self.fig.canvas.draw()
        renderer=self.fig.canvas.get_renderer()
        x0,x1=self.ax.get_xlim();y0,y1=self.ax.get_ylim()
        for artist,node in self.labels:
            b=artist.get_window_extent(renderer).transformed(self.ax.transData.inverted())
            if b.x0<x0-.02 or b.x1>x1+.02 or b.y0<y0-.02 or b.y1>y1+.02:
                raise ValueError(name+': clipped label '+repr(artist.get_text()))
            if node and (b.x0<node[0]-.02 or b.x1>node[2]+.02 or b.y0<node[1]-.02 or b.y1>node[3]+.02):
                raise ValueError(name+': label exceeds node '+repr(artist.get_text()))
        self.fig.savefig(out/(name+'.pdf'),format='pdf',
                         metadata={'Creator':'Python Matplotlib','Producer':None,
                                   'CreationDate':None,'ModDate':None})
        plt.close(self.fig)

def data_gate(out):
    d = Drawing((0, 0, 12.8, 5.7))
    d.box('p', 2.0, 4.3, 3.3, 1.0, r'$p:\mathrm{src}(a)$'+'\n'+r'ready at $r_p$')
    d.box('q', 2.0, 2.4, 3.3, 1.0, r'$q:\mathrm{src}(b)$'+'\n'+r'ready at $r_q$')
    d.box('copy', 8.0, 3.35, 1.3, 1.3, 'copy', shape='circle')
    d.edge('p', 'copy', 'e', 'w')
    d.edge('q', 'copy', 'e', 'w', dashed=True)
    d.text(5.4, 4.25, 'data, delay 0')
    d.text(5.4, 2.3, 'gate, delay 0')
    d.arrow(d.point('copy','e'), (10.6, 3.35))
    d.text(11.6, 3.35, r'$\mathrm{src}(a)$')
    d.text(6.4, .8, 'solid: payload and timing;  dashed: timing only')
    d.save(out, 'data-gate')


def row_cover(out):
    d = Drawing((0, 0, 14.2, 5.1))
    for side, x in [('A',2.5), ('B',11.7)]:
        d.frame(x-2.15, 1.4, 4.3, 2.6)
    for name,x,y,label in [
        ('a1',2.5,3.3,r'$A_a=(2,4,3)$'),
        ('a2',2.5,2.1,r'$A_b=(1,3,5)$'),
        ('b1',11.7,3.3,r'$B_a=(2,5,5)$'),
        ('b2',11.7,2.1,r'$B_b=(3,4,4)$')]:
        d.box(name,x,y,3.6,.75,label)
    d.edge('a1','b1','e','w'); d.text(7.1,3.65,'covered')
    d.edge('a2','b1','e','w'); d.text(7.1,2.95,'covered')
    d.edge('a2','b2','e','w',dashed=True)
    d.text(7.1,1.75,'not coordinatewise')
    d.text(2.5,4.55,r'$\Omega$: payload $\mathrm{pair}(\mathrm{src}(a),\mathrm{src}(b))$',size=8.5)
    d.text(11.7,4.55,r'$\Gamma$: same opaque payload',size=8.5)
    d.save(out, 'row-cover')


def residual(out):
    d = Drawing((0,0,14.2,5.7))
    d.box('u',1.1,3.1,.95,.95,'$u$',shape='circle')
    d.ax.patches[-1].set_facecolor('0.9')
    d.box('v1',5.3,4.25,.95,.95,'$v_1$',shape='circle')
    d.box('v2',5.3,1.95,.95,.95,'$v_2$',shape='circle')
    d.edge('u','v1','e','w');d.edge('u','v2','e','w')
    d.text(4.0,4.7,'received');d.text(4.0,1.35,'in flight')
    d.line(((2.8,.8),(2.8,5.0)),dashed=True)
    d.text(2.8,5.35,r'cut $\tau$')
    d.box('buffered',10.0,4.25,4.7,1.0,'buffered port\nready 0')
    d.box('crossing',10.0,1.95,4.7,1.0,r'$c_{(u,v_2)}$'+'\n'+'positive ready interval')
    d.edge('v1','buffered','e','w',dashed=True)
    d.edge('v2','crossing','e','w',dashed=True)
    d.arrow(d.point('buffered','e'),(13.5,4.25))
    d.arrow(d.point('crossing','e'),(13.5,1.95))
    d.save(out,'residual')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='Direct Python renderers for the three semantic schematics.')
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    for renderer in (data_gate,row_cover,residual):
        renderer(args.output)


