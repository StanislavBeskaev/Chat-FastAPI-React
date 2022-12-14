import React from 'react'
import {Button} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import searchMessagesStore from '../../stores/searchMessagesStore'


const MessagesSearch = () => {
  const count = searchMessagesStore.getCount()
  const current = searchMessagesStore.getCurrent()
  const searchText = searchMessagesStore.getSearchText()

  const handleKeyPress = e => {
    if (e.key === 'Enter') searchMessagesStore.increaseCurrent()
  }

  return (
    <>
      {
        count
          ? <div className="d-flex gap-2 align-items-center">
              <span>{current + 1}/{count}</span>
              <Button
                variant="light"
                size="sm"
                onClick={() => searchMessagesStore.decreaseCurrent()}
              >
                &#8593;
              </Button>
              <Button
                variant="light"
                size="sm"
                onClick={() => searchMessagesStore.increaseCurrent()}
              >
                &#8595;
              </Button>
            </div>
          : searchText
              ? <span className="text-warning">{current}/{count}</span>
              : null
      }
      <input
        type="text"
        placeholder="поиск сообщений"
        value={searchText}
        onKeyPress={handleKeyPress}
        onChange={e => searchMessagesStore.setSearchText(e.target.value)}
        style={{paddingLeft: 7, width: 175}}
      />
    </>
  )
}

export default observer(MessagesSearch)