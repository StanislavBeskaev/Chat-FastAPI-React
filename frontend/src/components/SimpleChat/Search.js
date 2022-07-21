import React from 'react'
import {Button} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import searchMessagesStore from '../../stores/searchMessagesStore'


const Search = () => {
  const count = searchMessagesStore.getCount()
  const current = searchMessagesStore.getCurrent()
  const searchText = searchMessagesStore.getSearchText()

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
        value={searchText}
        // TODO сделать перемотку по Enter
        onChange={e => searchMessagesStore.setSearchText(e.target.value)}
      />
    </>
  )
}

export default observer(Search)