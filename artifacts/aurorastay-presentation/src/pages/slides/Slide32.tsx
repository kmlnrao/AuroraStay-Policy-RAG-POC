import React, { useState, useEffect, useRef } from "react";
import img_1 from "./assets/images/image_1.png";
import img_2 from "./assets/images/image_2.png";
import img_3 from "./assets/images/image_3.png";
const Slide32: React.FC = () => {
  const outerRef = useRef<HTMLDivElement>(null);
  const [layout, setLayout] = useState({
    s: 1,
    x: 0,
    y: 0
  });
  useEffect(() => {
    const el = outerRef.current;
    if (!el) return;
    const update = () => {
      const w = el.clientWidth;
      const h = el.clientHeight;
      const s = Math.min(w / 960, h / 540);
      setLayout({
        s,
        x: (w - 960 * s) / 2,
        y: (h - 540 * s) / 2
      });
    };
    update();
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  return <div id="slide-32" ref={outerRef} className="w-screen h-screen overflow-hidden relative" style={{
    backgroundColor: "#000"
  }}><div id="slide-inner-32" style={{
      position: "absolute",
      width: "960px",
      height: "540px",
      overflow: "hidden",
      transformOrigin: "top left",
      color: "#000000",
      backgroundColor: "#ffffff",
      transform: `scale(${layout.s})`,
      left: layout.x + "px",
      top: layout.y + "px"
    }}><div key={0} style={{
        position: "absolute",
        left: "234.58px",
        top: "516.29px",
        width: "490.83px",
        height: "28.94px",
        boxSizing: "border-box",
        backgroundColor: "transparent",
        padding: "9.6px 9.6px 9.6px 9.6px",
        wordWrap: "break-word"
      }}><p style={{
          textAlign: "center",
          lineHeight: "1.23",
          paddingLeft: "1.33px",
          fontSize: "calc(7pt * var(--pptx-font-scale, 1))",
          marginTop: "0",
          marginBottom: "0"
        }}><span style={{
            fontSize: "calc(7pt * var(--pptx-font-scale, 1))",
            fontFamily: "'Nunito', sans-serif",
            fontWeight: "700",
            color: "#434343"
          }}>{"Proprietary content. \xA9 Great Learning. All Rights Reserved. Unauthorized use or distribution prohibited."}</span></p></div><img key={1} src={img_1} alt="Google Shape;119;p25" style={{
        position: "absolute",
        left: "805.2px",
        top: "7.17px",
        width: "146.51px",
        height: "60.13px",
        boxSizing: "border-box",
        objectFit: "fill"
      }} /><div key={2} style={{
        position: "absolute",
        left: "0.69px",
        top: "0px",
        width: "18.43px",
        height: "74.46px"
      }}><div key={0} style={{
          position: "absolute",
          left: "0px",
          top: "0px",
          width: "18.43px",
          height: "37.32px",
          boxSizing: "border-box",
          backgroundColor: "#0E39A9"
        }} /><div key={1} style={{
          position: "absolute",
          left: "0px",
          top: "37.14px",
          width: "18.43px",
          height: "37.32px",
          boxSizing: "border-box",
          backgroundColor: "#1974D2"
        }} /></div><div key={3} style={{
        position: "absolute",
        left: "0px",
        top: "-0.04px",
        width: "960.06px",
        height: "540.03px",
        boxSizing: "border-box",
        backgroundColor: "#0E39A9"
      }} /><div key={4} style={{
        position: "absolute",
        left: "635.44px",
        top: "54.01px",
        width: "219.96px",
        height: "388.8px",
        boxSizing: "border-box",
        overflow: "hidden"
      }}><img src={img_2} alt="A close up of a logo&#xA;&#xA;Description automatically generated" style={{
          position: "absolute",
          left: "-473.49px",
          top: "-114.23px",
          width: "1105.88px",
          height: "622.15px",
          maxWidth: "none"
        }} /></div><div key={5} style={{
        position: "absolute",
        left: "35.12px",
        top: "175.98px",
        width: "459.09px",
        height: "188px",
        boxSizing: "border-box",
        backgroundColor: "transparent",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        padding: "3.6px 7.2px 3.6px 7.2px",
        wordWrap: "break-word"
      }}><p style={{
          textAlign: "left",
          lineHeight: "1.08",
          fontSize: "calc(33pt * var(--pptx-font-scale, 1))",
          marginTop: "0",
          marginBottom: "0"
        }}><span style={{
            fontSize: "calc(33pt * var(--pptx-font-scale, 1))",
            fontFamily: "'Nunito ExtraBold', 'Nunito', sans-serif",
            fontWeight: "800",
            color: "#ffffff"
          }}>{"Thank You"}</span></p></div><img key={6} src={img_3} alt="Google Shape;128;p26" style={{
        position: "absolute",
        left: "44.29px",
        top: "80.83px",
        width: "322.46px",
        height: "132.42px",
        boxSizing: "border-box",
        objectFit: "fill"
      }} /><div key={7} style={{
        position: "absolute",
        left: "7.36px",
        top: "703.75px",
        width: "1575.72px",
        height: "73.26px",
        boxSizing: "border-box",
        backgroundColor: "transparent"
      }} /><div key={8} style={{
        position: "absolute",
        left: "898.35px",
        top: "498.67px",
        width: "57.61px",
        height: "41.32px",
        boxSizing: "border-box",
        backgroundColor: "transparent",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        padding: "9.6px 9.6px 9.6px 9.6px",
        wordWrap: "break-word"
      }}><p style={{
          textAlign: "center",
          lineHeight: "1.2",
          fontSize: "calc(14pt * var(--pptx-font-scale, 1))",
          marginTop: "0",
          marginBottom: "0"
        }}><span style={{
            fontSize: "calc(14pt * var(--pptx-font-scale, 1))",
            fontFamily: "Arial, 'Helvetica Neue', sans-serif",
            color: "#000000"
          }}>{"32"}</span></p></div></div></div>;
};
export default Slide32;
