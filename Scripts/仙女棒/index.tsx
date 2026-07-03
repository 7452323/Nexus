import {Script,Navigation,NavigationStack,Button,Text,HStack,VStack,ZStack,Grid,GridRow,Spacer,Image,RoundedRectangle,useState,useRef,useEffect} from "scripting"

const LEVELS = [
  {id:1,name:"轻抚",intensity:0.2,sharpness:0.1},
  {id:2,name:"吞息",intensity:0.35,sharpness:0.2},
  {id:3,name:"沉浸",intensity:0.5,sharpness:0.4},
  {id:4,name:"失重",intensity:0.7,sharpness:0.5},
  {id:5,name:"震颤",intensity:0.85,sharpness:0.8},
  {id:6,name:"余潮",intensity:1.0,sharpness:1.0},
]

function View(){
  const dismiss=Navigation.useDismiss()
  const [enabled,setEnabled]=useState(false)
  const [active,setActive]=useState(LEVELS[3])
  const timer=useRef<number>()
  const running=useRef(false)

  function stop(){running.current=false;setEnabled(false);if(timer.current!=null){clearTimeout(timer.current);timer.current=undefined}}
  
  function runPattern(level:typeof LEVELS[0]){
    if(timer.current!=null)clearTimeout(timer.current)
    running.current=true
    async function tick(){
      if(!running.current)return
      try{await Haptics.continuous(0.9,level.intensity,level.sharpness)}finally{if(!running.current)return;timer.current=setTimeout(()=>{void tick()},20)} 
    }
    void tick()
  }

  function handleToggle(v:boolean){if(v){setEnabled(true);runPattern(active)}else{stop()}}
  function handleLevel(l:typeof LEVELS[0]){setActive(l);if(enabled||running.current){setEnabled(true);runPattern(l)}}

  useEffect(()=>{return()=>{running.current=false;if(timer.current!=null)clearTimeout(timer.current)}},[])

  return(
    <NavigationStack>
      <ZStack background={{colors:["#020308","#0a1020","#161d30","#090d16"],startPoint:"topLeading",endPoint:"bottomTrailing"}}>
        <VStack spacing={22} padding={20} frame={{maxWidth:'infinity',maxHeight:'infinity',alignment:'center'}}>
          <Spacer minLength={120}/>
          <Grid>
            <GridRow>
              <Button action={()=>handleLevel(LEVELS[0])}><Text>{LEVELS[0].name}</Text></Button>
              <Button action={()=>handleLevel(LEVELS[1])}><Text>{LEVELS[1].name}</Text></Button>
            </GridRow>
            <GridRow>
              <Button action={()=>handleLevel(LEVELS[2])}><Text>{LEVELS[2].name}</Text></Button>
              <Button action={()=>handleLevel(LEVELS[3])}><Text>{LEVELS[3].name}</Text></Button>
            </GridRow>
            <GridRow>
              <Button action={()=>handleLevel(LEVELS[4])}><Text>{LEVELS[4].name}</Text></Button>
              <Button action={()=>handleLevel(LEVELS[5])}><Text>{LEVELS[5].name}</Text></Button>
            </GridRow>
          </Grid>
          <Spacer/>
          <HStack spacing={12}>
            <Button title="开启" action={()=>handleToggle(true)}/>
            <Button title="停止" action={()=>handleToggle(false)}/>
          </HStack>
        </VStack>
      </ZStack>
    </NavigationStack>
  )
}

async function run(){await Navigation.present(<View/>);Script.exit()}
run()
