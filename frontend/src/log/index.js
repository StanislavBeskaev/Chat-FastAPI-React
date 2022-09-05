export default function logMessages(...messages) {
  if (process.env.NODE_ENV === 'development' || ["1", "true", 'yes', 'on'].indexOf(window.__ENV__.FRONTEND_DEBUG_MODE.toLowerCase()) > -1) {
    console.log(...messages)
  }
}
