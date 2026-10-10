"""Two-page Chinese review; all researcher signatures remain blank."""
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Spacer,PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[3];DOC=ROOT/'docs/reduction/rapid_reduction';RESULT=ROOT/'results/reduction/rapid_v1'
pdfmetrics.registerFont(TTFont('GUVReviewFont','C:/Windows/Fonts/simsun.ttc',subfontIndex=0))
body=ParagraphStyle('body',fontName='GUVReviewFont',fontSize=9,leading=13,wordWrap='CJK',textColor=colors.HexColor('#243647'),spaceAfter=6)
small=ParagraphStyle('small',parent=body,fontSize=8,leading=11,spaceAfter=0)
title=ParagraphStyle('title',parent=body,fontSize=17,leading=22,spaceAfter=13,textColor=colors.HexColor('#174b70'))
head=ParagraphStyle('head',parent=body,fontSize=11,leading=15,spaceBefore=9,spaceAfter=6)
def p(s,style=body):return Paragraph(escape(s).replace('\n','<br/>'),style)
def table(data,widths):
    t=Table([[p(str(x),small) for x in row] for row in data],colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4edf3')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#ccd7df')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));return t
def footer(c,doc):
    c.setFont('GUVReviewFont',8);c.setFillColor(colors.HexColor('#667b8b'));c.drawString(36,25,'PURE / PNAS2017 | 本地研究证据 | HUMAN_REVIEW_REQUIRED');c.drawRightString(A4[0]-36,25,str(doc.page))
def main():
    summary=json.loads((RESULT/'model_summary.json').read_text(encoding='utf-8'));audit=json.loads((RESULT/'b1_3_fresh_audit.json').read_text(encoding='utf-8'));W=A4[0]-72
    flow=[p('B1-3 + Phase C：研究者科学决策',title),p('01 / B1-3 独立复核与源结构',head),p('34条保存历史已独立重算：逐事件Petri、有限非负库存、载体DAG与S_full*w均通过。旧26个B1-3文件保持原始字节。AI建议不是研究者签署；继承B1-2 H3/H4/H6条件继续有效。')]
    rows=[['项','AI建议','原始源证据与仍有效的条件','研究者决定']]
    abbreviated=['0796/0811：W4末态与两支源入口连续。','0796/0797/0811/0812：同一入口token竞争，可逆重新选择非同时双产物。','0798/0813：各唯一自由Pept0003，RF-bound终止态分别保留。','0799/0814直接释放；RF3-GDP交换路径至0847。有限GTP供应，RF3_GDP非自由RF3+GDP。','0910分成bound-50S及termRS30S_mRNA；0911/0913/0916/0918随后释放。额外EFG-GTP非内源再生。','0016/0077/0902：直接联合6PO4；RF3交换联合7。源种账本不是完整元素/电荷证书。','0797/0812/0810/0823及回收逆向保留；作者零模式非普适删除。','字面源身份与生理、分子组成解释分开；完整模型尚未获科学批准。','Gly两轮聚合为近似；回收尾部商系统对保护边际闭合，两维微观相关性丢失。']
    for row,text in zip(audit['review'],abbreviated):rows.append([row['id'],row['AI_recommendation'],text,'________'])
    flow+=[table(rows,[33,77,W-176,66]),Spacer(1,9),p('允许选择：Y / N / CONDITIONAL / NEED_MORE_EVIDENCE。研究者备注：'),p('__________________________________________________________________'),p('依据：b1_3_independent_scientific_audit.md；逐事件源方程、资源库存和新鲜审查在b1_3_fresh_audit.json。历史36个负对照未重生成；MATLAB 99/3/1未重跑。',small),PageBreak(),p('02 / Phase C：限定域候选决策',head)]
    flow.append(table([['候选','删除与闭合依据；实际验证','AI建议 / 研究者决定'],['R1：214维','27个SOURCE_GENERAL守恒关系，全部968列与可逆重构证明；数值通过。','接受数学限定范围 / ____'],['R2：175维','36恒零种、205支持、30独立关系；rank175。完整源状态可唯一恢复。','接受固定作者零模式与初值支持面 / ____'],['Gly1：174维\nGly1+2：173维','0017+0018、0078+0079各吸收一个fast态，kb=7000/1007；局部及四场景长期PASS。','条件接受 / ____ / ____'],['回收：173维','七态至N3/N2与三因子边际；k=1000，0306/0910输入保留；精确保护观测商系统。','条件接受；不恢复微观相关性 / ____'],['组合：171维','组合重新耦合四场景PASS。20计数器独立报告；边际资源/占用保留。','条件接受长期域 / ____']],[85,W-232,147]))
    flow+=[p('必须保留的失败边界',head),p('非零fast局部初值的初始层资源误差可达10%，不能宣称全初始层精确。fast=1/freeTuGDP=0的投影库存为负，BLOCKED。0952零旁支重激活时R0/R1完成，R2/R3超域BLOCKED。RF1/RF2合并有0.5/1.5导数反例。旧21态QSSA及四循环全稳态不能作为成功候选。',small),p('简化效果：四场景最大长期固定尺度误差',head)]
    rows=[['指标','Full','Exact','Author Exact','Topology']];picked=[next(r for r in summary if r['model']==m) for m in ['R0','R1','R2','R3_CHAIN12_RECYCLE']]
    rows.append(['化学维数 / 减少']+[f"{r['independent_dimension']} / {r['reduction_vs_241_percent']:.2f}%" for r in picked]);rows.append(['中位秒 / 相对速度']+[f"{r['median_seconds']:.3f} / {r['speedup']:.3f}x" for r in picked]);rows.append(['肽 / 资源误差']+['参考' if not r['maxima_long'] else f"{r['maxima_long']['peptide_max']*100:.3g}% / {r['maxima_long']['resource_max']*100:.3g}%" for r in picked]);rows.append(['证据类型','收敛参考','精确可逆','作者域精确可逆','耦合长期门PASS'])
    flow+=[table(rows,[100]+[(W-100)/4]*4),Spacer(1,7),p('组合累计误差0.0464469%，通量RMS0.00115311%；无加速。严格完整源状态最大精确减少为175维；173维回收为观测商系统。Gross ATP/GTP计数含自由池可逆结合，不等于水解次数。',small),p('人工签署与另行发布授权',head),p('逐项接受 / 条件 / 拒绝 / 补充验证：___________________________________',small),p('范围条件：________________________________________________________',small),p('研究者 / 日期：____________________________________________________',small),p('Commit：允许 / 不允许 ____；Push：允许 / 不允许 ____。本次均未尝试。',small)]
    path=DOC/'review_and_decision.pdf';SimpleDocTemplate(str(path),pagesize=A4,rightMargin=36,leftMargin=36,topMargin=34,bottomMargin=40,title='B1-3 + Phase C researcher decision',author='Local scientific evidence; unsigned').build(flow,onFirstPage=footer,onLaterPages=footer)
    reader=PdfReader(path);assert len(reader.pages)==2,len(reader.pages);(RESULT/'decision_pdf_check.json').write_text(json.dumps({'pages':2,'all_researcher_decisions':'BLANK','content_source':'review_and_decision.md and saved validation/audit','path':str(path)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Two-page PDF generated; awaiting rendered visual check.')
if __name__=='__main__':main()
