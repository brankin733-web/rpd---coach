import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "com.rpdfootball.coach",
  appName: "RPD Coach",
  webDir: "www",
  server: {
    url: "https://rpd-coach.brankin733.chatgpt.site",
    cleartext: false,
    allowNavigation: ["rpd-coach.brankin733.chatgpt.site"]
  },
  android: {
    backgroundColor: "#080a0c",
    allowMixedContent: false
  }
};

export default config;
