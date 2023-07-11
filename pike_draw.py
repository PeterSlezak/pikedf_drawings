import pikepdf

#-------------------------------------------------------------------------------
#
# ADD SIMPLE DRAWINGS CAPABILITY TO PIKEPDF Page object
#
#-------------------------------------------------------------------------------
def color_code(c: list, f: str) -> str:
    ''' create RGB color code PDF command for fill f = 'f' or stroke f = 'c' operation '''
    
    if type(c) is not list \
        or len(c) != 3 \
        or min(c) < 0 \
        or max(c) > 1:
        raise ValueError("RGB color needs 3 color components in range 0 to 1")
        
    return f"{c[0]} {c[1]} {c[2]} RG " if f == "c" else f"{c[0]} {c[1]} {c[2]} rg "


class MyPage(pikepdf.Page):

    def draw_line(self, start_point: list, end_point: list,
                  border_width: int = 0, stroke_color: list=None, dash_pattern: str = None,
                  line_join_style: int = 0, line_cap_style: int = 0):
        '''
        Draw a line on page
        start_point    - Point where the line starts [x, y]
        end_point      - Point where the line ends [x, y]
        border_width   - A line width of 0 denotes the thinnest line that can be rendered at device resolution:
                         1 device pixel wide. However, some devices cannot reproduce 1-pixel lines, and on
                         high-resolution devices, they are nearly invisible. Since the results of rendering such
                         zero-width lines are device-dependent, their use is not recommended.
        dash_pattern   - The line dash pattern controls the pattern of dashes and gaps used to stroke paths.
                         It is specified by a dash array and a dash phase. The dash array’s elements are
                         numbers that specify the lengths of alternating dashes and gaps; the numbers
                         must be nonnegative and not all zero.
                         e.g. "[ 2 1 ] 0" means 2 on, 1 off, 2 on, 1 off ...
                              "[ 2 1 ] 1" means 1 on, 1 off, 2 on, 1 off ...
        stroke_color    - Color in RGB
        line_join_style - 0 = Miter join, 1 = Round join, 2 = Bevel join
        line_cap_style  - 0 = Butt cap, 1 = Round cap, 2 = Projecting square cap
        '''


        if border_width < 0:
            raise ValueError("border_width must be non-negative")
        if line_join_style not in [0, 1, 2]:
            raise ValueError("line_join_style value must be 0, 1, or 2")
        if line_cap_style not in [0, 1, 2]:
            raise ValueError("line_cap_style value must be 0, 1, or 2")

        if stroke_color is not None:
           all_color_str = color_code(stroke_color, 'c')
        else: #BLACK
           all_color_str = color_code([0, 0, 0], 'c')
        all_color_str += 'S'

        if dash_pattern is not None:
            dash_pattern_str = dash_pattern + " d"
        else:
            dash_pattern_str = ' '

        #Content stream template for the line drawing
        line_stream_str = f'''
        q
        {start_point[0]} {start_point[1]} m
        {end_point[0]} {end_point[1]} l
        {border_width} w
        h
        {line_join_style} j
        {line_cap_style} J
        {dash_pattern_str}
        {all_color_str}
        Q
        '''

        self.contents_add(bytes(line_stream_str, 'ascii'))
        
    
    def draw_rect(self, point: list, width: float, height: float,
                  border_width: int = 0, stroke_color: list=None, dash_pattern: str = None,
                  fill_color: list=None,
                  line_join_style: int = 0, line_cap_style: int = 0):
        '''
        Draw a rectangle on page
        point          - lower-left rectangle corner [x, y]
        width          - rectangle width. 
        height         - rectangle height
        border_width   - A line width of 0 denotes the thinnest line that can be rendered at device resolution:
                         1 device pixel wide. However, some devices cannot reproduce 1-pixel lines, and on
                         high-resolution devices, they are nearly invisible. Since the results of rendering such
                         zero-width lines are device-dependent, their use is not recommended.
        dash_pattern   - The line dash pattern controls the pattern of dashes and gaps used to stroke paths.
                         It is specified by a dash array and a dash phase. The dash array’s elements are
                         numbers that specify the lengths of alternating dashes and gaps; the numbers
                         must be nonnegative and not all zero.
                         e.g. "[ 2 1 ] 0" means 2 on, 1 off, 2 on, 1 off ...
                              "[ 2 1 ] 1" means 1 on, 1 off, 2 on, 1 off ...
        stroke_color    - Color in RGB
        fill_color      - Color in RGB
        line_join_style - 0 = Miter join, 1 = Round join, 2 = Bevel join
        line_cap_style  - 0 = Butt cap, 1 = Round cap, 2 = Projecting square cap
        '''

        if border_width < 0:
            raise ValueError("border_width must be non-negative")
        if line_join_style not in [0, 1, 2]:
            raise ValueError("line_join_style value must be 0, 1, or 2")
        if line_cap_style not in [0, 1, 2]:
            raise ValueError("line_cap_style value must be 0, 1, or 2")

        #TODO: check validity of the dash_pattern value
        #TODO: check validity of the point
        
        all_color_str = ''
        if fill_color is not None and stroke_color is not None:
            all_color_str = color_code(fill_color, 'f') + color_code(stroke_color, 'c') + 'B\n'
        elif fill_color is not None:
            all_color_str = color_code(fill_color, 'f') + 'f\n'
        elif stroke_color is not None:
            all_color_str = color_code(stroke_color, 'c') + '\n'
        elif stroke_color is None: #BLACK
            all_color_str = color_code([0, 0, 0], 'c') + '\n'

        all_color_str += 'S'

        
        if dash_pattern is not None:
            dash_pattern_str = dash_pattern + " d"
        else:
            dash_pattern_str = ' '

        #Content stream template for the rectangle drawing    
        rect_stream_str = f'''
        q
        {point[0]} {point[1]} {width} {height} re
        {border_width} w
        h
        {line_join_style} j
        {line_cap_style} J
        {dash_pattern_str}
        {all_color_str}
        Q
        '''
        
        self.contents_add(bytes(rect_stream_str, 'ascii'))





if __name__ == '__main__':
    print(pikepdf.__version__)

    outpath = r"ex_drawings.pdf"
    
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    pg_height = pdf.pages[0].mediabox[3]
    
    MyPage(pdf.pages[0]).draw_rect([10,pg_height-110], 50, 100, border_width=5.0, stroke_color=[0, 1, 0], dash_pattern="[2 2] 0", line_join_style=1)
    MyPage(pdf.pages[0]).draw_rect([100,pg_height-110], 50, 100, border_width=5.0, fill_color=[1, 0, 0], stroke_color=[0, 0, 0])
    MyPage(pdf.pages[0]).draw_rect([200,pg_height-110], 100, 20, border_width=5.0, stroke_color=[0, 1, 0], fill_color=[1, 0, 0], line_join_style=2)
    MyPage(pdf.pages[0]).draw_rect([400,pg_height-110], 50, 50, border_width=0, fill_color=[1, 0, 0], line_join_style=0)

    MyPage(pdf.pages[0]).draw_line([10,pg_height-150], [300, pg_height-400],
                                   border_width=2,
                                   dash_pattern="[2 5] 0",
                                   stroke_color=[0, 1, 1],
                                   line_join_style=1,
                                   line_cap_style=1)

    pdf.save(outpath, compress_streams=False, normalize_content=True, qdf=True)
    pdf.close()
