/**
 * 学习资料 - 看书 & 听书
 * 数据源: https://yazhouse8.com
 */

import {
  useState, useEffect, useMemo, useCallback, createContext, useContext, useRef,
  VStack, HStack, ZStack, Text, Image, Button, List, Section, ScrollView, ForEach,
  NavigationStack, NavigationLink, Spacer, LazyVGrid, TextField, ProgressView,
  TabView, Tab, fetch, Picker, Menu, Toggle, Slider,
  Navigation, Script, gradient, RoundedRectangle, Rectangle
} from "scripting"

const BASE_URL = "https://yazhouse8.com"

const READING_CATEGORIES = [
  {id:"1",name:"都市激情",url:"/article.php?cate=1"},
  {id:"2",name:"人妻交换",url:"/article.php?cate=2"},
  {id:"3",name:"校园春色",url:"/article.php?cate=3"},
  {id:"4",name:"家庭乱伦",url:"/article.php?cate=4"},
]

const AUDIO_CATEGORIES = [
  {id:"long",name:"长篇",icon:"book.fill"},
  {id:"short",name:"短篇",icon:"text.justify"},
]

interface ArticleInfo {id:string;title:string;category?:string}
interface AudioBookInfo {id:string;title:string;type:"long"|"short"}
interface TrackInfo {id:string;bookId:string;title:string;audioUrl:string}
