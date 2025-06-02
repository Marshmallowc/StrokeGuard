import {
	createSSRApp
} from "vue";
import App from "./App.vue";
import api from "./utils/api";
import store from "./store";

export function createApp() {
	const app = createSSRApp(App);
	
	// 全局挂载API和状态管理
	app.config.globalProperties.$api = api;
	app.config.globalProperties.$store = store;
	
	return {
		app,
	};
}
