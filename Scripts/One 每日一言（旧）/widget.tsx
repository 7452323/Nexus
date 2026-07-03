import { VStack, ZStack, Text, Image, Spacer, Widget, fetch } from 'scripting'

const API_BASE = 'http://v3.wufazhuce.com:8000/api'
const CACHE_KEY = 'one_content'

interface ContentItem {
  title: string
  forward: string
  img_url: string
}

function formatDate(): string {
  const now = new Date()
  return `${String(now.getDate()).padStart(2,'0')}/${String(now.getMonth()+1).padStart(2,'0')}`
}

function WidgetView({content}: {content:ContentItem}) {
  const isSmall = Widget.family === 'systemSmall'
  return (
    <ZStack>
      <Image imageUrl={content.img_url} resizable aspectRatio={{contentMode:'fill'}} frame={{width:Widget.displaySize.width,height:Widget.displaySize.height}} clipped />
      <VStack>
        <Text font={isSmall?10:11} foregroundStyle='rgba(255,255,255,0.92)' padding={{horizontal:isSmall?8:12,vertical:isSmall?4:6}} shadow={{color:'rgba(0,0,0,0.5)',radius:1.5,y:1}}>{formatDate()}</Text>
        <Spacer />
        <VStack padding={{horizontal:isSmall?10:14,vertical:isSmall?8:10}}>
          <Text font={isSmall?10:13} foregroundStyle='rgba(255,255,255,0.92)' lineLimit={isSmall?6:5} shadow={{color:'rgba(0,0,0,0.5)',radius:1.5,y:1}}>{content.forward}</Text>
        </VStack>
      </VStack>
    </ZStack>
  )
}

async function main() {
  try {
    const idListResp = await fetch(`${API_BASE}/onelist/idlist`)
    const idListData = await idListResp.json()
    const ids:string[] = idListData.data
    if (ids?.length) {
      const contentResp = await fetch(`${API_BASE}/onelist/${ids[0]}/0`)
      const contentData = await contentResp.json()
      if (contentData.res === 0 && contentData.data?.content_list?.length) {
        const content = contentData.data.content_list[0] as ContentItem
        Storage.set(CACHE_KEY, JSON.stringify(content))
        Widget.present(<WidgetView content={content} />, {reloadPolicy:{policy:'after',date:new Date(Date.now()+1000*60*60*3)}})
        return
      }
    }
  } catch {}
  const cached = Storage.get<string>(CACHE_KEY)
  if (cached) {
    try {
      Widget.present(<WidgetView content={JSON.parse(cached)} />, {reloadPolicy:{policy:'after',date:new Date(Date.now()+1000*60*30)}})
      return
    } catch {}
  }
  Widget.present(<VStack background='rgba(0,0,0,0.8)' padding><Text font={14} foregroundStyle='rgba(255,255,255,0.6)'>ONE·一个</Text><Text font={11} foregroundStyle='rgba(255,255,255,0.4)'>暂无内容</Text></VStack>, {reloadPolicy:{policy:'after',date:new Date(Date.now()+1000*60*5)}})
}
main()
