# Web-Scrapying-practice

爬蟲小練習

1. USA SEC Litigation Release(2011~2020)
   - 說明：爬取美國證管會發佈的訴訟新聞稿，製成excel後作為後續text mining的材料
   - 使用工具：BeautifulSoup
   - 遭遇問題：每段時期的文章html都不太相同，年份越早，文章元素越是以不規律方式存放，導致各元素爬取正確率下降，後續進行調整

2. Yahoo Finance News (wordcloud)
   - 說明：爬取奇摩財經新聞，排除廣告文章，進行分詞＆過濾停用字後，計算各關鍵字的字頻並以文字雲方式呈現
   - 使用工具：selenium、jieba、wordcloud

3. 104 job bank
   - 說明：爬取104人力銀行“數據分析”的職缺內容並彙整成一份excel檔
   - 使用工具：selenium、
   - 遭遇問題：因為網頁使用JS render而無法直接爬取，因此透過app觀看模式來取得html

4. Taiwan Receipt Lottery
   - 說明：爬取財政部統一發票的每期號碼並提供兌獎功能，主要用於Azure LineChatBot，在OCR光學辨識發票號碼後進行兌獎服務
   - 使用工具：BeautifulSoup
