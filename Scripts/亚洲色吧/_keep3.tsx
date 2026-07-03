// LibraryView - 书库（收藏）

function LibraryView() {
  const ctx = useContext(AppContext)
  const [subTab, setSubTab] = useState<"articles"|"audio">("articles")

  return (
    <NavigationStack>
      <VStack navigationTitle={'书库'} spacing={0}>
        <HStack padding={{horizontal:16,vertical:8}} spacing={16}>
          <Button action={()=>setSubTab("articles")}><Text>文章</Text></Button>
          <Button action={()=>setSubTab("audio")}><Text>听书</Text></Button>
        </HStack>
        {subTab==='articles'?(
          (ctx?.favArticles.length??0)===0?(
            <VStack alignment={'center'}><Text>还没有收藏文章</Text></VStack>
          ):(
            <ScrollView>{(ctx?.favArticles??[]).map(a=><NavigationLink key={a.id} destination={<ArticleReaderView article={a}/>}><Text>{a.title}</Text></NavigationLink>)}</ScrollView>
          )
        ):(
          (ctx?.favAudio.length??0)===0?(
            <VStack alignment={'center'}><Text>还没有收藏听书</Text></VStack>
          ):(
            <List>{(ctx?.favAudio??[]).map(b=><NavigationLink key={b.id} destination={<TrackListView book={b}/>}><Text>{b.title}</Text></NavigationLink>)}</List>
          )
        )}
      </VStack>
    </NavigationStack>
  )
}

// HistoryView - 历史
function HistoryView() {
  return (
    <NavigationStack>
      <List navigationTitle={'历史'}>
        <Text>暂无历史记录</Text>
      </List>
    </NavigationStack>
  )
}

// SettingsView - 设置
function SettingsView() {
  return (
    <NavigationStack>
      <List navigationTitle={'设置'}>
        <Text>设置页面</Text>
      </List>
    </NavigationStack>
  )
}

function App() {
  return (
    <TabView>
      <Tab title="看书" systemImage="book.fill" value={0}><NavigationStack><Text>看书</Text></NavigationStack></Tab>
      <Tab title="听书" systemImage="headphones" value={1}><NavigationStack><Text>听书</Text></NavigationStack></Tab>
      <Tab title="书库" systemImage="books.vertical" value={2}><LibraryView/></Tab>
      <Tab title="历史" systemImage="clock" value={3}><HistoryView/></Tab>
      <Tab title="设置" systemImage="gearshape" value={4}><SettingsView/></Tab>
    </TabView>
  )
}

async function run() {
  await Navigation.present({element:<App/>,modalPresentationStyle:"overFullScreen"})
  Script.exit()
}
run()
