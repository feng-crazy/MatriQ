export default {
  pages: [
    'pages/index/index',
    'pages/pipeline-list/index',
    'pages/pipeline-detail/index',
    'pages/pipeline-new/index',
  ],
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#667eea',
    navigationBarTitleText: 'MatriQ',
    navigationBarTextStyle: 'white',
  },
  tabBar: {
    color: '#7A7E83',
    selectedColor: '#667eea',
    backgroundColor: '#ffffff',
    borderStyle: 'black',
    list: [
      {
        pagePath: 'pages/index/index',
        text: '首页',
        iconPath: 'src/assets/home.png',
        selectedIconPath: 'src/assets/home-active.png',
      },
      {
        pagePath: 'pages/pipeline-list/index',
        text: '流水线',
        iconPath: 'src/assets/list.png',
        selectedIconPath: 'src/assets/list-active.png',
      },
    ],
  },
}

