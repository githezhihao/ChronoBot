def user_bubble_html(content, time_str):
    return (
        '<div style="margin:18px 0 18px 0; overflow:auto;">'
        '<div style="float:right; clear:both; position:relative; display:inline-block;">'
        '<div style="background:#A0D8FF; color:#222; padding:12px 20px; border-radius:18px 4px 18px 18px; font-size:16px; min-width:40px; max-width:320px; word-break:break-all; box-shadow:0 2px 8px #b3e0ff55; border:1px solid #8CC8F6; position:relative; display:inline-block;">'
        f'{content}'
        '<span style="position:absolute;right:-12px;bottom:10px;width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:12px solid #A0D8FF;"></span>'
        f'<span style="position:absolute;right:0;bottom:-18px;color:#b0b0b0;font-size:12px;">{time_str}</span>'
        '</div>'
        '</div>'
        '</div>'
    )

def ai_bubble_html(content, time_str):
    return (
        '<div style="margin:18px 0 18px 0; overflow:auto;">'
        '<div style="float:left; clear:both; position:relative; display:inline-block;">'
        '<div style="background:#fff; color:#222; padding:12px 20px; border-radius:4px 18px 18px 18px; font-size:16px; min-width:40px; max-width:320px; word-break:break-all; box-shadow:0 2px 8px #e5e6eb55; border:1px solid #E5E6EB; position:relative; display:inline-block;">'
        f'{content}'
        '<span style="position:absolute;left:-12px;bottom:10px;width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-right:12px solid #fff;border-left:none;"></span>'
        f'<span style="position:absolute;left:0;bottom:-18px;color:#b0b0b0;font-size:12px;">{time_str}</span>'
        '</div>'
        '</div>'
        '</div>'
    )
