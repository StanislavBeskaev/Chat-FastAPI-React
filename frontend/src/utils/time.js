export default function formatDate(strDate) {
  // Формат даты дд.мм.гг чч:мм
  const date = new Date(strDate)
  const year = date.getFullYear().toString().slice(2)
  const day = withLeadZero(date.getDate())
  const month = withLeadZero(date.getMonth() + 1)
  const hours = withLeadZero(date.getHours())
  const minutes = withLeadZero(date.getMinutes())
  return `${day}.${month}.${year} ${hours}:${minutes}`
}

function withLeadZero(number) {
  return number >= 10 ? number : `0${number}`
}
