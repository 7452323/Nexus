import {Script,Intent,fetch} from "scripting"

async function run() {
  const term = (Intent.shortcutParameter?.value?.toString()||Intent.textsParameter?.[0]||'').trim()
  if(!term){Script.exit(Intent.text('请输入App名称'));return}
  try {
    const encoded = encodeURIComponent(term)
    const resp = await fetch(`https://itunes.apple.com/search?term=${encoded}&entity=software&country=cn&limit=10`)
    if(!resp.ok){Script.exit(Intent.text(`搜索失败`));return}
    const data = await resp.json()
    const results = (data.results||[]).filter((r:any)=>r.trackId&&r.bundleId)
    if(results.length===0){Script.exit(Intent.text(`未找到匹配的App`));return}
    const lines = results.map((app:any,i:number)=>`${i+1}. ${app.trackName}\n   Bundle: ${app.bundleId}`)
    Script.exit(Intent.text(`搜索结果:${lines.join('\n\n')}`))
  } catch(err:any){Script.exit(Intent.text(`搜索失败:${err.message}`))}
}
run()
