你好，我是徐昊。通过前面的项目练习，我们完成了DI Container的功能。从这节课开始，我们就进入RESTful Web Services的开发。

## 整体功能介绍

在DI Container的部分，我们参考了Jakarta Dependency Injection作为功能依据。在RESTful Web Services部分，我们将会参考Jakarta RESTful Web Services。

Jakarta RESTful Web Services的功能比Jakarta Dependency Injection要庞杂一些，如视频中所演示的，我将从三个部分来讲解说明：

经过多年发展，Jakarta RESTful Web Services也变得日渐复杂，其中有些“高级”特性很少应用，在我们的项目中需要做一些取舍：

那么下面这段代码展示了我们需要实现的主要功能，并提供了相应的扩展能力：

```
public class UserOrdersResource {
    private User user;
    @Context
    private Orders orders;
    @Context
    private Products products;
    public UserOrdersResource(User user) {
        this.user = user;
    }
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public CollectionModel<Order> all() {
        return CollectionModel.of(orders.findBy(user.getId()))
                .add(Link.of("/users/{id}/orders").expand(user.getId().value()),
                        Link.of("/users/{id}", "owner").expand(user.getId().value()));
    }
    @GET
    @Path("/{id}")
    @Produces(MediaType.APPLICATION_JSON)
    public EntityModel<Order> findBy(@PathParam("id") long id) {
        return orders.findBy(user.getId(), new Order.Id(id))
                .map(o -> EntityModel.of(o)
                        .add(Link.of("/users/{id}/orders/{id}").expand(user.getId().value(), id),
                                Link.of("/users/{id}", "owner").expand(user.getId().value())))
                .orElse(null);
    }
    @POST
    @Consumes(MediaType.APPLICATION_FORM_URLENCODED)
    public Response placeOrder(@FormParam("item") List<Long> items, @FormParam("quantity") List<Double> quantities) {
        List<Product> products = this.products.find(items.stream().map(Product.Id::new).toList());
        Map<Product, Double> orderItems = new HashMap<>();
        for (int i = 0; i < products.size(); i++)
            orderItems.put(products.get(i), quantities.get(i));
        Order order = orders.create(user, orderItems);
        return Response.created(Link.of("/users/{uid}/orders/{oid}").expand(user.getId().value(), order.getId().value()).toUri()).build();
    }
}

public class UserResource {
    private User user;
    public UserResource(User user) {
        this.user = user;
    }
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public EntityModel<User> get() {
        return EntityModel.of(user).add(Link.of("/users/{value}").expand(user.getId().value()));
    }
    @Path("/orders")
    public UserOrdersResource orders(@Context ResourceContext context) {
        return context.initResource(new UserOrdersResource(user));
    }
}

@Path("/users")
public class UsersResource {
    @Context
    private Users users;
    @Path("{id}")
    public UserResource findById(@PathParam("id") User.Id id) {
        return users.findById(id).map(UserResource::new).orElse(null);
    }
    @POST
    @Consumes(MediaType.APPLICATION_FORM_URLENCODED)
    public Response register(@FormParam("name") String name, @FormParam("email") String email) {
        User user = users.create(name, email);
        return Response.created(Link.of("/users/{id}").expand(user.getId().value()).toUri()).build();
    }
}

```

我们很容易可以发现，RESTful Web Services需要多模块协同完成。而不是像DI Container那样，可以从单一模块入手，完成几个功能之后再进行重构。所以对于RESTful Web Services，伦敦学派或许是一种更好的方式。

那么下节课，我们将从伦敦学派入手，开始RESTful Web Services的开发。

## 思考题

按照视频中所展示的需求，我们要设计怎样的架构愿景，才能顺利地进入伦敦学派的开发？

欢迎把你的想法分享在留言区，也欢迎把你的项目代码分享出来。相信经过你的思考与实操，学习效果会更好！