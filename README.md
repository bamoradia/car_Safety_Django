# Car Safety Backend Server


## This API is to be used to get consolidated car crash safety information from both the NHTSA and IIHS. The API can return information to help the user narrow down which car they would like to search and then also provide the crash test rating information from both organizations as well as all active recalls on that specific vehicle.


## End Points

### GET https://boiling-harbor-89487.herokuapp.com/api/v1/topsafety

#### This endpoint returns a list of all IIHS top safety pick+ vehicles that are stored in our local database. It returns an object with a status key, as well as a data key.

#### Data is an object with keys of 'nhtsa', 'recall', and 'iihs'.

###### Each key in data is an array, and each element in the object provides the full information for that vehicle.




