
// レスポンシブデザインテストスクリプト
// ブラウザの開発者ツールで実行してください

function testResponsiveDesign() {
  const viewports = [
    { width: 375, height: 667, name: 'Mobile' },
    { width: 768, height: 1024, name: 'Tablet' },
    { width: 1024, height: 768, name: 'Landscape Tablet' },
    { width: 1920, height: 1080, name: 'Desktop' }
  ];

  console.log('🚀 レスポンシブデザインテスト開始');

  viewports.forEach(viewport => {
    console.log(`\n📱 ${viewport.name} (${viewport.width}x${viewport.height})`);
    
    // ビューポートサイズを設定
    window.resizeTo(viewport.width, viewport.height);
    
    // 基本的な要素の存在確認
    const body = document.body;
    const main = document.querySelector('main');
    const nav = document.querySelector('nav');
    
    console.log(`  ✅ Body: ${body ? '存在' : '不存在'}`);
    console.log(`  ✅ Main: ${main ? '存在' : '不存在'}`);
    console.log(`  ✅ Navigation: ${nav ? '存在' : '不存在'}`);
    
    // レスポンシブクラスの確認
    const responsiveClasses = body.className.match(/sm:|md:|lg:|xl:/g);
    if (responsiveClasses) {
      console.log(`  📱 レスポンシブクラス: ${responsiveClasses.join(', ')}`);
    }
  });

  console.log('\n🎉 レスポンシブデザインテスト完了');
}

// テスト実行
testResponsiveDesign();
