import argparse
import logging

import numpy as np

from Map import *
from AStar import *
from RRT import *

if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(
        level=logging.DEBUG, 
        datefmt="%Y-%m-%d %H:%M:%S",
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s'
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--map", type=str, default="asd.jpg", 
        help="path of map")
    parser.add_argument("--RRT", action="store_true", 
        help="apply RRT algorithm")
    parser.add_argument("--init", type=str, default="50,528",
        help="tuple of init position")
    parser.add_argument("--goal", type=str, default="730,30",
        help="tuple of goal position")
    parser.add_argument("--sample_prob", type=float, default=0.2,
        help="random sample probability in RRT algorithm")
    parser.add_argument("--upper_limit", type=int, default=50000,
        help="maximum sample times")
    parser.add_argument("--pixel_step", type=int, default=60,
        help="pixel movement per sample step")
    args = parser.parse_args()

    if args.RRT:
        logger.info("start applying RRT algorithm")

        logger.info("constructing map...Wait!")
        if args.init is not None and args.goal is not None:
            init = tuple(map(int, args.init.split(',')))
            goal = tuple(map(int, args.goal.split(',')))
            mmap = Map(args.map, init, goal)
        else:
            mmap = Map(args.map)
        logger.info("MAP CONSTRUCT SUCCESS")
        
        logger.info("executing RRT algorithm...Wait!")
        pixel_step = args.pixel_step
        sample_prob = args.sample_prob
        upper_limit = args.upper_limit
        vertices, edges, mmap = RRT(mmap, pixel_step, sample_prob, upper_limit)
        if vertices is None:
            logger.info("RRT ALGORITHM FAIL")
        else:
            logger.info("RRT ALGORITHM SUCCESS")
            logger.info("executing AStar search...Wait!")
            mmap, new_hists = AStar(vertices, edges, mmap)
            logger.info("ASTAR SEARCH SUCCESS")

        f = open('road.txt', 'w', encoding='utf-8')
        for node in new_hists:
            print(node[0], node[1], file=f)
        f.close()
        
        logger.info("saving map...Wait!")
        output_path = "{}-{}-{}.jpg".format(pixel_step, sample_prob, upper_limit)
        mmap.save_fig(output_path)
        logger.info("RRT algorithm has finished. Map has already saved in {}".format(output_path))