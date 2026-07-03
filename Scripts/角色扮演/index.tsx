import {Script,Navigation,NavigationStack,ScrollView,VStack,HStack,ZStack,Text,Image,Spacer,Button,gradient,useState,useEffect,AppEvents} from "scripting"
import {characters,Character} from "./characters"

function CharacterCard({character,onSelect}:{character:Character;onSelect:()=>void}){
  return(
    <Button action={onSelect}>
      <HStack padding={20} spacing={16} glassEffect={UIGlass.regular()} clipShape={{type:"rect",cornerRadius:24}}>
        <ZStack frame={{width:56,height:56}} background={(character.accentColor+"20") as any} clipShape={{type:"rect",cornerRadius:28}} alignment="center">
          <Image systemName={character.icon} font={24} foregroundStyle={character.accentColor as any}/>
        </ZStack>
        <VStack spacing={4} alignment="leading">
          <Text font={20} fontWeight="semibold">{character.name}</Text>
          <Text font={14} foregroundStyle="secondaryLabel">{character.description}</Text>
        </VStack>
        <Spacer/>
        <Image systemName="chevron.right" font={14} foregroundStyle="tertiaryLabel"/>
      </HStack>
    </Button>
  )}

function CharacterSelectionView(){
  const dismiss=Navigation.useDismiss()
  const [scheme,setScheme]=useState<"light"|"dark">("light")
  useEffect(()=>{AppEvents.colorScheme.addListener((ns)=>{setScheme(ns)})},[])
  const isDark=scheme==="dark"
  
  async function handleSelectCharacter(character:Character){
    try{
      if(Assistant.hasActiveConversation)await Assistant.stopConversation()
      await Assistant.startConversation({message:"你好！",systemPrompt:character.systemPrompt,autoStart:true})
      await Assistant.present()
      dismiss()
    }catch(e){console.error(String(e))}
  }

  return(
    <NavigationStack>
      <ZStack alignment="top">
        <ZStack background={gradient("linear",{colors:isDark?["#1a1a2e","#162447","#0f3460"]:["#f2f2f7","#eaeaef","#dce0e8"],startPoint:{x:0,y:0},endPoint:{x:0,y:1}})} frame={{maxWidth:"infinity",maxHeight:"infinity"}}/>
        <ScrollView>
          <VStack spacing={24} padding={20}>
            <VStack spacing={8} alignment="leading" padding={{top:50,bottom:8}}>
              <Text font={34} fontWeight="bold">角色扮演</Text>
              <Text font={15} foregroundStyle="secondaryLabel">选一个角色，开启属于你的故事</Text>
            </VStack>
            {characters.map(c=><CharacterCard key={c.id} character={c} onSelect={()=>handleSelectCharacter(c)}/>)}
            <Spacer minLength={60}/>
          </VStack>
        </ScrollView>
      </ZStack>
    </NavigationStack>
  )
}

export async function run(){await Navigation.present(<CharacterSelectionView/>);Script.exit()}
run()
