import {useState,useEffect,useMemo,useCallback,createContext,useContext,useRef,VStack,HStack,ZStack,Text,Image,Button,List,Section,ScrollView,ForEach,NavigationStack,NavigationLink,Spacer,LazyVGrid,TextField,ProgressView,TabView,Tab,fetch,Picker,Menu,Toggle,Slider,ScrollViewReader,ScrollViewProxy,Navigation,Script,gradient,RoundedRectangle,Rectangle} from "scripting"

const BASE_URL="https://yazhouse8.com"

const READING_CATEGORIES=[
  {id:"1",name:"都市激情",url:"/article.php?cate=1"},{id:"2",name:"人妻交换",url:"/article.php?cate=2"},{id:"3",name:"校园春色",url:"/article.php?cate=3"},{id:"4",name:"家庭乱伦",url:"/article.php?cate=4"},{id:"5",name:"情色笑话",url:"/article.php?cate=5"},{id:"6",name:"性爱技巧",url:"/article.php?cate=6"},{id:"7",name:"另类小说",url:"/article.php?cate=7"},{id:"8",name:"乱伦文章",url:"/article.php?cate=8"},{id:"9",name:"纪实小说",url:"/article.php?cate=9"},{id:"10",name:"武侠小说",url:"/article.php?cate=10"},{id:"11",name:"虐待小说",url:"/article.php?cate=11"},{id:"12",name:"两性话题",url:"/article.php?cate=12"},{id:"siwa",name:"丝袜小说",url:"/l9kdK.htm"},{id:"mijian",name:"迷奸小说",url:"/Ryuid.htm"},{id:"tiaojiao",name:"调教小说",url:"/KGl2i.htm"},{id:"lunjian",name:"轮奸小说",url:"/6pmJE.htm"},{id:"shoujiao",name:"兽交小说",url:"/BmwSt.htm"},{id:"luchu",name:"露出小说",url:"/thguq.htm"},{id:"xingnu",name:"性奴小说",url:"/McpCg.htm"},{id:"juru",name:"巨乳小说",url:"/sxUlc.htm"}]

const AppContext=createContext<any>()

function CategoryGrid(){
  return(<ScrollView navigationTitle="看书"><LazyVGrid columns={[{size:{type:'adaptive' as const,min:80},spacing:10}]} padding={16} spacing={10}>{READING_CATEGORIES.map(cat=><NavigationLink key={cat.id} destination={<VStack><Text>文章列表</Text></VStack>}><Text>{cat.name}</Text></NavigationLink>)}</LazyVGrid></ScrollView>)
}

function App(){
  return(<TabView><Tab title="看书" systemImage="book.fill" value={0}><CategoryGrid/></Tab><Tab title="听书" systemImage="headphones" value={1}><Text>听书</Text></Tab><Tab title="书库" systemImage="books.vertical" value={2}><Text>书库</Text></Tab><Tab title="历史" systemImage="clock" value={3}><Text>历史</Text></Tab><Tab title="设置" systemImage="gearshape" value={4}><Text>设置</Text></Tab></TabView>)
}

async function run(){await Navigation.present({element:<App/>,modalPresentationStyle:"overFullScreen"});Script.exit()}
run()
